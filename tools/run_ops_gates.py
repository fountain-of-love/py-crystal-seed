#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_module() -> object:
    module_name = "guardrails_ops.ops"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        local_src = REPO_ROOT / "libs" / "guardrails-ops" / "src"
        if local_src.exists() and str(local_src) not in sys.path:
            sys.path.insert(0, str(local_src))
        return importlib.import_module(module_name)


module = _load_module()


def _discover_root_package(src_root: Path) -> str:
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


def _load_greet() -> Callable[[], str]:
    root_package = _discover_root_package(SRC_ROOT)
    if not root_package:
        raise RuntimeError("unable to resolve root package for ops gate")
    app_module = importlib.import_module(f"{root_package}.main")
    greet = getattr(app_module, "greet", None)
    if not callable(greet):
        raise RuntimeError(f"{root_package}.main.greet is missing or not callable")
    return greet


def _run_local_hook(argv: list[str]) -> int:
    try:
        hooks = importlib.import_module("project_governance.hooks")
    except ModuleNotFoundError as exc:
        if exc.name in {"project_governance", "project_governance.hooks"}:
            return 0
        raise
    hook = getattr(hooks, "run_ops_gates", None)
    if not callable(hook):
        return 0
    result = cast(Callable[[Path, list[str]], int | None], hook)(REPO_ROOT, argv)
    return 0 if result is None else int(result)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run operational hardening gates (performance, leak, recovery, observability)."
    )
    parser.add_argument("--perf-iterations", type=int, default=20000)
    parser.add_argument("--perf-max-ms", type=float, default=0.02)
    parser.add_argument("--leak-iterations", type=int, default=25000)
    parser.add_argument("--leak-max-growth-kb", type=int, default=64)
    parser.add_argument("--recovery-max-retries", type=int, default=4)
    return parser.parse_args(argv)


if __name__ == "__main__":
    argv = sys.argv[1:]
    args = _parse_args(argv)
    try:
        greet_fn = _load_greet()
    except RuntimeError as exc:
        print(f"[ops-gate] {exc}")
        sys.exit(1)
    central_rc = int(
        module.run_ops_gates(
            greet_fn=greet_fn,
            perf_iterations=args.perf_iterations,
            perf_max_ms=args.perf_max_ms,
            leak_iterations=args.leak_iterations,
            leak_max_growth_kb=args.leak_max_growth_kb,
            recovery_max_retries=args.recovery_max_retries,
        )
    )
    if central_rc != 0:
        raise SystemExit(central_rc)
    raise SystemExit(_run_local_hook(argv))
