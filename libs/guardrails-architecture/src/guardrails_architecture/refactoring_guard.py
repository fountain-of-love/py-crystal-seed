from __future__ import annotations

import ast
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

import yaml

from .result import GuardResult

DEFAULT_CONFIG = "tools/refactoring_guardrails.yml"


class GuardConfig(dict[str, Any]):
    pass


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if path.is_file():
            yield path


def _discover_root_package(src_root: Path) -> str:
    if not src_root.exists():
        return ""
    packages = [
        child.name
        for child in src_root.iterdir()
        if child.is_dir()
        and (child / "__init__.py").exists()
        and not child.name.startswith("guardrails_")
    ]
    if len(packages) == 1:
        return packages[0]
    return ""


def _string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise RuntimeError(f"{name} must be a list of strings")
    return cast(list[str], value)


def _load_config(config_path: Path) -> GuardConfig:
    if not config_path.exists():
        return GuardConfig(
            {
                "version": 1,
                "include": ["src"],
                "ignore": [],
                "rules": {
                    "ban_wildcard_imports": True,
                    "max_relative_import_level": 1,
                    "detect_internal_cycles": True,
                    "cycle_roots": [],
                    "directional_dependencies": [],
                    "forbid_concrete_imports": [],
                    "composition_roots": [],
                    "allow_concrete_wiring_only_in": [],
                },
            }
        )

    payload_obj: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("config must be a mapping")
    payload = cast(dict[str, Any], payload_obj)

    version = payload.get("version", 1)
    if version != 1:
        raise RuntimeError("config version must be 1")

    include_items = _string_list(payload.get("include", ["src"]), "include")
    ignore_items = _string_list(payload.get("ignore", []), "ignore")
    rules_raw = payload.get("rules", {})
    if not isinstance(rules_raw, dict):
        raise RuntimeError("rules must be a mapping")
    rules = cast(dict[str, Any], rules_raw)

    directional_rules: list[dict[str, Any]] = []
    for index, rule in enumerate(cast(list[Any], rules.get("directional_dependencies", []))):
        if not isinstance(rule, dict):
            raise RuntimeError(f"directional_dependencies[{index}] must be a mapping")
        from_scope = rule.get("from", "")
        may_import = rule.get("may_import", [])
        if not isinstance(from_scope, str) or not from_scope.strip():
            raise RuntimeError(f"directional_dependencies[{index}].from must be a non-empty string")
        directional_rules.append(
            {
                "from": from_scope.strip(),
                "may_import": _string_list(may_import, f"directional_dependencies[{index}].may_import"),
            }
        )

    concrete_rules: list[dict[str, Any]] = []
    for index, rule in enumerate(cast(list[Any], rules.get("forbid_concrete_imports", []))):
        if not isinstance(rule, dict):
            raise RuntimeError(f"forbid_concrete_imports[{index}] must be a mapping")
        scope = rule.get("scope", "")
        forbidden_prefixes = rule.get("forbidden_prefixes", [])
        if not isinstance(scope, str) or not scope.strip():
            raise RuntimeError(f"forbid_concrete_imports[{index}].scope must be a non-empty string")
        concrete_rules.append(
            {
                "scope": scope.strip(),
                "forbidden_prefixes": _string_list(
                    forbidden_prefixes,
                    f"forbid_concrete_imports[{index}].forbidden_prefixes",
                ),
            }
        )

    return GuardConfig(
        {
            "version": 1,
            "include": include_items,
            "ignore": ignore_items,
            "rules": {
                "ban_wildcard_imports": bool(rules.get("ban_wildcard_imports", True)),
                "max_relative_import_level": int(rules.get("max_relative_import_level", 1)),
                "detect_internal_cycles": bool(rules.get("detect_internal_cycles", True)),
                "cycle_roots": [
                    item for item in _string_list(rules.get("cycle_roots", []), "rules.cycle_roots") if item
                ],
                "directional_dependencies": directional_rules,
                "forbid_concrete_imports": concrete_rules,
                "composition_roots": [
                    item for item in _string_list(rules.get("composition_roots", []), "rules.composition_roots") if item
                ],
                "allow_concrete_wiring_only_in": [
                    item
                    for item in _string_list(
                        rules.get("allow_concrete_wiring_only_in", []),
                        "rules.allow_concrete_wiring_only_in",
                    )
                    if item
                ],
            },
        }
    )


def _iter_scoped_files(repo_root: Path, config: GuardConfig) -> Iterable[Path]:
    ignore_patterns = cast(list[str], config["ignore"])
    for rel_root in cast(list[str], config["include"]):
        root = (repo_root / rel_root).resolve()
        if not root.exists():
            continue
        for file_path in _iter_python_files(root):
            rel = file_path.relative_to(repo_root)
            if any(rel.match(pattern) for pattern in ignore_patterns):
                continue
            yield file_path


def _module_name_for(file_path: Path, repo_root: Path) -> str:
    if file_path.suffix != ".py":
        return ""
    if "src" in file_path.parts:
        src_idx = file_path.parts.index("src")
        rel = Path(*file_path.parts[src_idx + 1 :]).with_suffix("")
    else:
        rel = file_path.relative_to(repo_root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_absolute_module(current_module: str, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    current_parts = current_module.split(".") if current_module else []
    if current_parts:
        current_parts = current_parts[:-1]
    steps_up = max(node.level - 1, 0)
    if steps_up > len(current_parts):
        return node.module or ""
    base_parts = current_parts[: len(current_parts) - steps_up]
    if node.module:
        base_parts.extend(node.module.split("."))
    return ".".join(base_parts)


def _collect_module_index(repo_root: Path, config: GuardConfig) -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for file_path in _iter_scoped_files(repo_root, config):
        module_name = _module_name_for(file_path, repo_root)
        if module_name:
            modules[module_name] = file_path
    return modules


def _candidate_targets(base_module: str, imported_name: str, module_index: dict[str, Path]) -> list[str]:
    candidates: list[str] = []
    direct = f"{base_module}.{imported_name}" if base_module else imported_name
    if direct in module_index:
        candidates.append(direct)
    if base_module in module_index:
        candidates.append(base_module)
    return candidates


def _detect_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    state: dict[str, int] = {}
    stack: list[str] = []
    seen_cycles: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(graph.get(node, set())):
            if state.get(neighbor, 0) == 0:
                visit(neighbor)
            elif state.get(neighbor) == 1:
                idx = stack.index(neighbor)
                cycle = stack[idx:] + [neighbor]
                key = tuple(cycle)
                if key not in seen_cycles:
                    seen_cycles.add(key)
                    cycles.append(cycle)
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def _scope_matches(module_name: str, scope: str) -> bool:
    return module_name == scope or module_name.startswith(f"{scope}.")


def _is_allowed_import(imported_module: str, source_scope: str, allowed: list[str]) -> bool:
    if _scope_matches(imported_module, source_scope):
        return True
    return any(_scope_matches(imported_module, candidate) for candidate in allowed)


def _concrete_import_forbidden(module_name: str, imported_module: str, rule: dict[str, Any], allowed_roots: list[str]) -> bool:
    scope = cast(str, rule["scope"])
    forbidden_prefixes = cast(list[str], rule["forbidden_prefixes"])
    if not _scope_matches(module_name, scope):
        return False
    if any(_scope_matches(module_name, allowed_root) for allowed_root in allowed_roots):
        return False
    return any(imported_module == prefix or imported_module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)


def check_refactoring_guard(*, repo_root: Path, config_path: Path) -> GuardResult:
    try:
        config = _load_config(config_path)
    except RuntimeError as exc:
        return GuardResult(guard="refactoring_guard", status="fail", violations=[{"message": str(exc)}])

    violations: list[str] = []
    module_index = _collect_module_index(repo_root, config)
    graph: dict[str, set[str]] = {module: set() for module in module_index}
    rules = cast(dict[str, Any], config["rules"])
    ban_wildcard_imports = bool(rules["ban_wildcard_imports"])
    max_relative_import_level = int(rules["max_relative_import_level"])
    detect_internal_cycles = bool(rules["detect_internal_cycles"])
    cycle_roots = cast(list[str], rules["cycle_roots"])
    directional_rules = cast(list[dict[str, Any]], rules["directional_dependencies"])
    concrete_rules = cast(list[dict[str, Any]], rules["forbid_concrete_imports"])
    allowed_concrete_roots = cast(list[str], rules["allow_concrete_wiring_only_in"])

    if not cycle_roots:
        src_root = repo_root / "src"
        root_package = _discover_root_package(src_root) if src_root.exists() else ""
        if root_package:
            cycle_roots = [root_package]

    directional_checks = 0
    concrete_checks = 0

    for module_name, file_path in module_index.items():
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError as exc:
            violations.append(f"{file_path}:{exc.lineno}: syntax error: {exc.msg}")
            continue

        for node in ast.walk(tree):
            imported_modules: list[str] = []
            if isinstance(node, ast.ImportFrom):
                if ban_wildcard_imports and any(alias.name == "*" for alias in node.names):
                    violations.append(f"{file_path}:{node.lineno}: wildcard imports are forbidden")
                if node.level > max_relative_import_level:
                    violations.append(
                        f"{file_path}:{node.lineno}: relative import level {node.level} exceeds allowed maximum {max_relative_import_level}"
                    )
                abs_module = _resolve_absolute_module(module_name, node)
                if abs_module:
                    imported_modules.append(abs_module)
                if detect_internal_cycles and abs_module:
                    for alias in node.names:
                        if alias.name == "*":
                            if abs_module in module_index:
                                graph[module_name].add(abs_module)
                            continue
                        for target in _candidate_targets(abs_module, alias.name, module_index):
                            graph[module_name].add(target)
            elif isinstance(node, ast.Import):
                imported_modules = [alias.name for alias in node.names]
                if detect_internal_cycles:
                    for imported in imported_modules:
                        if any(imported == root or imported.startswith(f"{root}.") for root in cycle_roots):
                            if imported in module_index:
                                graph[module_name].add(imported)

            for imported_module in imported_modules:
                for rule in directional_rules:
                    source_scope = cast(str, rule["from"])
                    if not _scope_matches(module_name, source_scope):
                        continue
                    directional_checks += 1
                    allowed = cast(list[str], rule["may_import"])
                    if not _is_allowed_import(imported_module, source_scope, allowed):
                        violations.append(
                            f"{file_path}:{getattr(node, 'lineno', 0)}: dependency direction violation: "
                            f"'{module_name}' may not import '{imported_module}' (allowed: {allowed})"
                        )
                for rule in concrete_rules:
                    concrete_checks += 1
                    if _concrete_import_forbidden(module_name, imported_module, rule, allowed_concrete_roots):
                        violations.append(
                            f"{file_path}:{getattr(node, 'lineno', 0)}: concrete import violation: "
                            f"'{module_name}' may not import '{imported_module}' outside composition roots"
                        )

    if detect_internal_cycles:
        scoped_graph: dict[str, set[str]] = {}
        for module_name, imports in graph.items():
            if not any(module_name == root or module_name.startswith(f"{root}.") for root in cycle_roots):
                continue
            scoped_graph[module_name] = {
                item for item in imports if any(item == root or item.startswith(f"{root}.") for root in cycle_roots)
            }
        for cycle in _detect_cycles(scoped_graph):
            violations.append("internal dependency cycle detected: " + " -> ".join(cycle))

    if violations:
        return GuardResult(
            guard="refactoring_guard",
            status="fail",
            violations=[{"message": item} for item in violations],
            metrics={
                "modules_scanned": len(module_index),
                "directional_rules_checked": directional_checks,
                "concrete_import_rules_checked": concrete_checks,
            },
        )

    return GuardResult(
        guard="refactoring_guard",
        status="pass",
        metrics={
            "modules_scanned": len(module_index),
            "directional_rules_checked": directional_checks,
            "concrete_import_rules_checked": concrete_checks,
        },
    )


def format_refactoring_guard_result(result: GuardResult) -> str:
    if result.status == "fail":
        lines = ["[refactoring-guard] Violations found:"]
        lines.extend(f"  - {item['message']}" for item in result.violations)
        return "\n".join(lines)
    return "[refactoring-guard] OK: no structural refactoring violations detected."


def run_refactoring_guard_check(*, repo_root: Path, config_path: Path) -> int:
    result = check_refactoring_guard(repo_root=repo_root, config_path=config_path)
    print(format_refactoring_guard_result(result))
    return result.exit_code()


def main() -> int:
    repo_root_env = os.getenv("REPO_ROOT", "").strip()
    repo_root = Path(repo_root_env).resolve() if repo_root_env else Path.cwd()

    config_env = os.getenv("REFACTORING_GUARD_FILE", "").strip() or DEFAULT_CONFIG
    config_path = Path(config_env)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()

    return run_refactoring_guard_check(repo_root=repo_root, config_path=config_path)
