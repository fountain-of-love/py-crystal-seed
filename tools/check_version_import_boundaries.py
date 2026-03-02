#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_module() -> Any:
    module_name = "guardrails_architecture.version_evolution"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        local_src = REPO_ROOT / "libs" / "guardrails-architecture" / "src"
        if local_src.exists() and str(local_src) not in sys.path:
            sys.path.insert(0, str(local_src))
        return importlib.import_module(module_name)


def _run_local_hook(argv: list[str]) -> int:
    try:
        hooks = importlib.import_module("project_governance.hooks")
    except ModuleNotFoundError as exc:
        if exc.name in {"project_governance", "project_governance.hooks"}:
            return 0
        raise
    hook = getattr(hooks, "check_version_evolution", None)
    if not callable(hook):
        return 0
    result = cast(Callable[[Path, list[str]], int | None], hook)(REPO_ROOT, argv)
    return 0 if result is None else int(result)


module = _load_module()

if __name__ == "__main__":
    argv = sys.argv[1:]
    central_rc = int(module.main(argv))
    if central_rc != 0:
        raise SystemExit(central_rc)
    raise SystemExit(_run_local_hook(argv))
