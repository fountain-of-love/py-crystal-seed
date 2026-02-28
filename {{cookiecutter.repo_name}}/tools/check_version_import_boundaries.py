#!/usr/bin/env python3
"""
Version evolution guardrail:
1) Cross-version import rule:
   block imports from v(N-1) internals inside vN modules.
2) Compatibility rule:
   core contracts used by lower versions must remain stable.

Contract file:
  tools/version_evolution_contracts.json
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path

VERSION_RE = re.compile(r"^v(\d+)$")
DEFAULT_CONTRACTS_FILE = "tools/version_evolution_contracts.json"


def _discover_root_package(src_dir: Path) -> str:
    packages = []
    if not src_dir.exists():
        return ""
    for child in src_dir.iterdir():
        if child.is_dir() and (child / "__init__.py").exists():
            packages.append(child.name)
    if len(packages) == 1:
        return packages[0]
    return ""


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if path.is_file():
            yield path


def _module_path(file_path: Path, src_root: Path) -> str:
    rel = file_path.relative_to(src_root).with_suffix("")
    return ".".join(rel.parts)


def _is_version_module(module_path: str, version_namespace: str) -> tuple[int, str] | None:
    parts = module_path.split(".")
    if version_namespace not in parts:
        return None
    ns_idx = parts.index(version_namespace)
    if ns_idx + 1 >= len(parts):
        return None
    version_token = parts[ns_idx + 1]
    match = VERSION_RE.match(version_token)
    if not match:
        return None
    return int(match.group(1)), ".".join(parts[: ns_idx + 2])


def _is_allowed_facade_symbol(symbol: str, prev_version: int) -> bool:
    if symbol == "facade":
        return True
    return symbol.endswith(f"_v{prev_version}")


def _check_prev_import(
    *,
    imported_module: str,
    imported_symbol: str | None,
    prev_base: str,
    prev_version: int,
) -> str | None:
    if imported_module == prev_base:
        if imported_symbol is None:
            return None
        if _is_allowed_facade_symbol(imported_symbol, prev_version):
            return None
        return f"forbidden symbol '{imported_symbol}' from previous version package '{prev_base}'"

    prefix = f"{prev_base}."
    if not imported_module.startswith(prefix):
        return None

    child = imported_module[len(prefix) :].split(".", 1)[0]
    if _is_allowed_facade_symbol(child, prev_version):
        return None
    return f"forbidden previous-version internal import '{imported_module}'"


def _signature_for_args(args: ast.arguments) -> str:
    parts: list[str] = []
    posonly = [arg.arg for arg in args.posonlyargs]
    normal = [arg.arg for arg in args.args]
    if posonly:
        parts.extend(posonly)
        parts.append("/")
    parts.extend(normal)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    elif args.kwonlyargs:
        parts.append("*")
    parts.extend(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return ",".join(parts)


def _class_signature(node: ast.ClassDef) -> str:
    method_signatures: list[str] = []
    bases = [ast.unparse(base) for base in node.bases]
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if child.name.startswith("_"):
                continue
            method_signatures.append(f"{child.name}({_signature_for_args(child.args)})")
    method_signatures.sort()
    return f"class[{','.join(bases)}]|methods[{';'.join(method_signatures)}]"


def _collect_core_signatures(
    *,
    src_root: Path,
    root_package: str,
    core_namespace: str,
) -> dict[str, str]:
    signatures: dict[str, str] = {}
    core_root = src_root / root_package / core_namespace
    if not core_root.exists():
        return signatures

    for file_path in _iter_python_files(core_root):
        rel = file_path.relative_to(core_root).with_suffix("")
        module_suffix = ".".join(rel.parts)
        if not module_suffix:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))

        public_symbols: list[str] = []
        for node in tree.body:
            is_function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            if is_function and not node.name.startswith("_"):
                public_symbols.append(node.name)
                signatures[f"{module_suffix}::{node.name}"] = (
                    f"func[{_signature_for_args(node.args)}]"
                )
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                public_symbols.append(node.name)
                signatures[f"{module_suffix}::{node.name}"] = _class_signature(node)

        public_symbols.sort()
        signatures[f"{module_suffix}::*"] = f"module[{','.join(public_symbols)}]"

    return signatures


def _collect_protected_core_keys(
    *,
    src_root: Path,
    root_package: str,
    version_namespace: str,
    core_namespace: str,
) -> set[str]:
    protected: set[str] = set()
    scan_root = src_root / root_package
    if not scan_root.exists():
        return protected

    version_files: list[tuple[int, Path]] = []
    for file_path in _iter_python_files(scan_root):
        mod_path = _module_path(file_path, src_root)
        info = _is_version_module(mod_path, version_namespace)
        if info:
            version_files.append((info[0], file_path))

    if not version_files:
        return protected
    max_version = max(version for version, _ in version_files)
    protected_versions = {version for version, _ in version_files if version <= max_version - 1}
    if not protected_versions:
        return protected

    core_base = f"{root_package}.{core_namespace}"
    core_prefix = f"{core_base}."
    for version, file_path in version_files:
        if version not in protected_versions:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    if imported.startswith(core_prefix):
                        suffix = imported[len(core_prefix) :]
                        protected.add(f"{suffix}::*")
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                if module_name == core_base:
                    for alias in node.names:
                        if alias.name != "*":
                            protected.add(f"{alias.name}::*")
                elif module_name.startswith(core_prefix):
                    suffix = module_name[len(core_prefix) :]
                    for alias in node.names:
                        if alias.name == "*":
                            protected.add(f"{suffix}::*")
                        else:
                            protected.add(f"{suffix}::{alias.name}")
    return protected


def _load_contract(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("protected_core_signatures", {})
    if not isinstance(raw, dict):
        raise RuntimeError("protected_core_signatures must be an object")
    return {str(key): str(value) for key, value in raw.items()}


def _write_contract(path: Path, signatures: dict[str, str]) -> None:
    payload = {
        "schema_version": 1,
        "protected_core_signatures": dict(sorted(signatures.items())),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check version import boundaries and core compatibility contracts."
    )
    parser.add_argument(
        "--write-contract",
        action="store_true",
        help="Write/refresh version evolution contracts and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])

    repo_root_env = os.getenv("REPO_ROOT", "").strip()
    repo_root = (
        Path(repo_root_env).resolve() if repo_root_env else Path(__file__).resolve().parents[1]
    )
    src_root = repo_root / "src"

    root_package = os.getenv("ROOT_PACKAGE", "").strip() or _discover_root_package(src_root)
    if not root_package:
        print("[evolution-guard] Skipped: could not determine root package.")
        return 0

    version_namespace = os.getenv("VERSION_NAMESPACE", "versions").strip() or "versions"
    core_namespace = os.getenv("CORE_NAMESPACE", "core").strip() or "core"
    contracts_env = os.getenv("EVOLUTION_CONTRACTS_FILE", DEFAULT_CONTRACTS_FILE).strip()
    contracts_file = Path(contracts_env or DEFAULT_CONTRACTS_FILE)
    if not contracts_file.is_absolute():
        contracts_file = (repo_root / contracts_file).resolve()

    scan_root = src_root / root_package
    boundary_violations: list[str] = []
    for file_path in _iter_python_files(scan_root):
        mod_path = _module_path(file_path, src_root)
        version_info = _is_version_module(mod_path, version_namespace)
        if not version_info:
            continue

        current_version, _ = version_info
        if current_version <= 1:
            continue
        prev_version = current_version - 1
        prev_base = f"{root_package}.{version_namespace}.v{prev_version}"

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError as exc:
            boundary_violations.append(f"{file_path}:{exc.lineno}: syntax error: {exc.msg}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    reason = _check_prev_import(
                        imported_module=alias.name,
                        imported_symbol=None,
                        prev_base=prev_base,
                        prev_version=prev_version,
                    )
                    if reason:
                        boundary_violations.append(f"{file_path}:{node.lineno}: {reason}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    reason = _check_prev_import(
                        imported_module=node.module,
                        imported_symbol=alias.name,
                        prev_base=prev_base,
                        prev_version=prev_version,
                    )
                    if reason:
                        boundary_violations.append(f"{file_path}:{node.lineno}: {reason}")

    protected_keys = _collect_protected_core_keys(
        src_root=src_root,
        root_package=root_package,
        version_namespace=version_namespace,
        core_namespace=core_namespace,
    )
    current_core_signatures = _collect_core_signatures(
        src_root=src_root,
        root_package=root_package,
        core_namespace=core_namespace,
    )
    protected_current_signatures = {
        key: current_core_signatures[key]
        for key in sorted(protected_keys)
        if key in current_core_signatures
    }

    if args.write_contract:
        _write_contract(contracts_file, protected_current_signatures)
        print(f"[evolution-guard] Contract written: {contracts_file}")
        return 0

    compatibility_violations: list[str] = []
    if protected_keys:
        if not contracts_file.exists():
            compatibility_violations.append(
                f"missing contracts file: {contracts_file} (run checker with --write-contract)"
            )
        else:
            try:
                baseline = _load_contract(contracts_file)
            except (json.JSONDecodeError, RuntimeError) as exc:
                compatibility_violations.append(f"invalid contracts file: {exc}")
                baseline = {}

            for key in sorted(protected_keys):
                if key not in current_core_signatures:
                    compatibility_violations.append(
                        f"protected core symbol missing in current code: {key}"
                    )
                    continue
                if key not in baseline:
                    compatibility_violations.append(
                        f"protected core symbol missing in contracts: {key}"
                    )
                    continue
                if baseline[key] != current_core_signatures[key]:
                    compatibility_violations.append(
                        "contract drift for "
                        f"{key}: baseline={baseline[key]!r} "
                        f"current={current_core_signatures[key]!r}"
                    )

    if boundary_violations:
        print("[import-boundary] Violations found:")
        for item in boundary_violations:
            print(f"  - {item}")
        print(
            "[import-boundary] Rule: vN may import only previous facade modules "
            "(facade or *_v(N-1)); previous internals are forbidden."
        )

    if compatibility_violations:
        print("[compatibility] Violations found:")
        for item in compatibility_violations:
            print(f"  - {item}")
        print(
            "[compatibility] Rule: core contracts used by lower versions are stable; "
            "extend/wrap/subclass instead of changing existing contracts."
        )

    if boundary_violations or compatibility_violations:
        return 1

    print("[evolution-guard] OK: import-boundary and compatibility checks passed.")
    if not protected_keys:
        print("[evolution-guard] No protected lower-version core contracts discovered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
