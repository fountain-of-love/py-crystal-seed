from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable
from pathlib import Path

from .ops import check_ops_gates, format_ops_result


def _discover_root_package(src_root: Path) -> str:
    packages = [
        child.name
        for child in src_root.iterdir()
        if child.is_dir() and (child / "__init__.py").exists() and not child.name.startswith("guardrails_")
    ]
    return packages[0] if len(packages) == 1 else ""


def _load_target(repo_root: Path, target: str) -> Callable[[], str]:
    if target:
        module_name, _, attr = target.partition(":")
        if not module_name or not attr:
            raise RuntimeError("target must be in module:function format")
        module = importlib.import_module(module_name)
        func = getattr(module, attr, None)
        if not callable(func):
            raise RuntimeError(f"{target} is missing or not callable")
        return func
    src_root = repo_root / "src"
    root_package = _discover_root_package(src_root)
    if not root_package:
        raise RuntimeError("unable to resolve root package for ops gate")
    module = importlib.import_module(f"{root_package}.main")
    func = getattr(module, "greet", None)
    if not callable(func):
        raise RuntimeError(f"{root_package}.main.greet is missing or not callable")
    return func


def run_ops_gates(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run operational hardening gates.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    parser.add_argument("--target", default="")
    parser.add_argument("--perf-iterations", type=int, default=20000)
    parser.add_argument("--perf-max-ms", type=float, default=0.02)
    parser.add_argument("--leak-iterations", type=int, default=25000)
    parser.add_argument("--leak-max-growth-kb", type=int, default=64)
    parser.add_argument("--recovery-max-retries", type=int, default=4)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))
    try:
        greet_fn = _load_target(repo_root, args.target)
    except RuntimeError as exc:
        print(f"[ops-gate] {exc}")
        return 1
    result = check_ops_gates(
        greet_fn=greet_fn,
        perf_iterations=args.perf_iterations,
        perf_max_ms=args.perf_max_ms,
        leak_iterations=args.leak_iterations,
        leak_max_growth_kb=args.leak_max_growth_kb,
        recovery_max_retries=args.recovery_max_retries,
    )
    print(result.to_json() if args.output == "json" else format_ops_result(result))
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(run_ops_gates(sys.argv[1:]))
