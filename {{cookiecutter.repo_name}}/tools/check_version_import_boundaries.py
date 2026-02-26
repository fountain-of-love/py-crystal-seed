#!/usr/bin/env python3
"""
Guardrail: block imports from v(N-1) internals inside vN modules.

Allowed:
- vN -> <root>.versions.v(N-1).facade
- vN -> <root>.versions.v(N-1).<name ending with _v(N-1)>

Forbidden:
- vN -> <root>.versions.v(N-1).<any other internal module>
- from <root>.versions.v(N-1) import <non-facade symbol>
"""

from __future__ import annotations

import ast
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path

VERSION_RE = re.compile(r"^v(\d+)$")


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


def _check_import(
    *,
    imported_module: str,
    imported_symbol: str | None,
    prev_base: str,
    prev_version: int,
) -> str | None:
    if imported_module == prev_base:
        # from pkg.versions.v5 import facade / livinglib_v5
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


def main() -> int:
    repo_root_env = os.getenv("REPO_ROOT", "").strip()
    repo_root = (
        Path(repo_root_env).resolve()
        if repo_root_env
        else Path(__file__).resolve().parents[1]
    )
    src_root = repo_root / "src"

    root_package = os.getenv("ROOT_PACKAGE", "").strip() or _discover_root_package(src_root)
    if not root_package:
        print("[import-boundary] Skipped: could not determine root package.")
        return 0

    version_namespace = os.getenv("VERSION_NAMESPACE", "versions").strip() or "versions"
    scan_root = src_root / root_package

    violations: list[str] = []
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
            violations.append(f"{file_path}:{exc.lineno}: syntax error: {exc.msg}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    reason = _check_import(
                        imported_module=alias.name,
                        imported_symbol=None,
                        prev_base=prev_base,
                        prev_version=prev_version,
                    )
                    if reason:
                        violations.append(f"{file_path}:{node.lineno}: {reason}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                for alias in node.names:
                    reason = _check_import(
                        imported_module=module_name,
                        imported_symbol=alias.name,
                        prev_base=prev_base,
                        prev_version=prev_version,
                    )
                    if reason:
                        violations.append(f"{file_path}:{node.lineno}: {reason}")

    if violations:
        print("[import-boundary] Violations found:")
        for item in violations:
            print(f"  - {item}")
        print(
            "[import-boundary] Rule: vN may import only previous facade modules "
            "(facade or *_v(N-1)); previous internals are forbidden."
        )
        return 1

    print("[import-boundary] OK: no forbidden previous-version internal imports detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
