from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any, cast

import yaml

DEFAULT_CONFIG = "tools/package_boundaries.yml"


def _iter_python_files(package_root: Path):
    for path in package_root.rglob("*.py"):
        if path.is_file():
            yield path


def _package_to_path(package: str) -> Path:
    return Path(*package.split("."))


def _is_forbidden(module: str, forbidden_prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)


def _load_rules(config_path: Path) -> list[tuple[str, tuple[str, ...]]]:
    if not config_path.exists():
        raise RuntimeError(f"config file not found: {config_path}")
    payload_obj: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("config must be a mapping")
    payload = cast(dict[str, Any], payload_obj)

    rules_obj = payload.get("rules", [])
    if not isinstance(rules_obj, list):
        raise RuntimeError("rules must be a list")
    raw_rules = cast(list[Any], rules_obj)

    rules: list[tuple[str, tuple[str, ...]]] = []
    for idx, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise RuntimeError(f"rule #{idx + 1} must be a mapping")
        rule = cast(dict[str, Any], raw)

        package_raw = rule.get("package", "")
        if not isinstance(package_raw, str):
            raise RuntimeError(f"rule #{idx + 1}: package must be a string")
        package = package_raw.strip()

        forbidden_obj = rule.get("forbidden_prefixes", [])
        forbidden_raw = cast(list[Any], forbidden_obj) if isinstance(forbidden_obj, list) else []
        if not package:
            raise RuntimeError(f"rule #{idx + 1}: package is required")
        if not forbidden_raw or not all(isinstance(x, str) and x.strip() for x in forbidden_raw):
            raise RuntimeError(
                f"rule #{idx + 1}: forbidden_prefixes must be a non-empty list of strings"
            )
        forbidden = tuple(item.strip() for item in forbidden_raw if isinstance(item, str))
        rules.append((package, forbidden))
    return rules


def run_package_boundary_check(
    *,
    repo_root: Path,
    config_path: Path,
) -> int:
    src_root = repo_root / "src"
    try:
        rules = _load_rules(config_path)
    except RuntimeError as exc:
        print(f"[package-boundary] {exc}")
        return 1

    if not rules:
        print("[package-boundary] No package boundary rules configured; skipping.")
        return 0

    violations: list[str] = []
    for package, forbidden in rules:
        package_root = src_root / _package_to_path(package)
        if not package_root.exists():
            continue
        for file_path in _iter_python_files(package_root):
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
            except SyntaxError as exc:
                violations.append(f"{file_path}:{exc.lineno}: syntax error: {exc.msg}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_forbidden(alias.name, forbidden):
                            violations.append(
                                f"{file_path}:{node.lineno}: forbidden import "
                                f"'{alias.name}' in package '{package}'"
                            )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if _is_forbidden(node.module, forbidden):
                        violations.append(
                            f"{file_path}:{node.lineno}: forbidden from-import "
                            f"'{node.module}' in package '{package}'"
                        )

    if violations:
        print("[package-boundary] Violations found:")
        for item in violations:
            print(f"  - {item}")
        return 1

    print("[package-boundary] OK: no forbidden cross-package imports detected.")
    return 0


def main() -> int:
    repo_root_env = os.getenv("REPO_ROOT", "").strip()
    repo_root = (
        Path(repo_root_env).resolve() if repo_root_env else Path.cwd()
    )

    config_env = os.getenv("PACKAGE_BOUNDARIES_FILE", "").strip() or DEFAULT_CONFIG
    config_path = Path(config_env)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()

    return run_package_boundary_check(repo_root=repo_root, config_path=config_path)
