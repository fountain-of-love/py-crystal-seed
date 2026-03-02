from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .package_boundaries import check_package_boundaries as _engine_check_package_boundaries
from .package_boundaries import format_package_boundary_result
from .refactoring_guard import check_refactoring_guard as _engine_check_refactoring_guard
from .refactoring_guard import format_refactoring_guard_result
from .version_evolution import check_version_evolution as _engine_check_version_evolution
from .version_evolution import format_version_evolution_result


def _repo_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    return parser


def check_package_boundaries_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate package boundary policy.")
    parser.add_argument("--config", default="tools/package_boundaries.yml")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    result = _engine_check_package_boundaries(repo_root=repo_root, config_path=config)
    print(result.to_json() if args.output == "json" else format_package_boundary_result(result))
    return result.exit_code()


def check_refactoring(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate refactoring guard policy.")
    parser.add_argument("--config", default="tools/refactoring_guardrails.yml")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    result = _engine_check_refactoring_guard(repo_root=repo_root, config_path=config)
    print(result.to_json() if args.output == "json" else format_refactoring_guard_result(result))
    return result.exit_code()


def check_version_evolution_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate version evolution policy.")
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--root-package", default="")
    parser.add_argument("--version-namespace", default="versions")
    parser.add_argument("--core-namespace", default="core")
    parser.add_argument("--contracts-file", default="tools/version_evolution_contracts.json")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    contracts = Path(args.contracts_file)
    if not contracts.is_absolute():
        contracts = (repo_root / contracts).resolve()
    src_root = repo_root / "src"
    root_package = args.root_package
    if not root_package and src_root.exists():
        packages = [child.name for child in src_root.iterdir() if child.is_dir() and (child / "__init__.py").exists() and not child.name.startswith("guardrails_")]
        root_package = packages[0] if len(packages) == 1 else ""
    result = _engine_check_version_evolution(
        repo_root=repo_root,
        root_package=root_package,
        version_namespace=args.version_namespace,
        core_namespace=args.core_namespace,
        contracts_file=contracts,
        write_contract=args.write_contract,
    )
    print(result.to_json() if args.output == "json" else format_version_evolution_result(result))
    return result.exit_code()


check_package_boundaries = check_package_boundaries_cli
check_version_evolution = check_version_evolution_cli

if __name__ == "__main__":
    raise SystemExit(check_version_evolution_cli(sys.argv[1:]))
