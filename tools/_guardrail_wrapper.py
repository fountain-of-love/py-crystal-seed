#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_repo_root() -> Path:
    repo_root = os.environ.get("REPO_ROOT", "").strip()
    if repo_root:
        return Path(repo_root).resolve()
    return Path.cwd().resolve()


def ensure_repo_on_path(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


def load_cli(module_name: str, fallback_src: Path) -> Any:
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        if fallback_src.exists():
            fallback_src_str = str(fallback_src)
            if fallback_src_str not in sys.path:
                sys.path.insert(0, fallback_src_str)
        return importlib.import_module(module_name)


def run_local_hook(repo_root: Path, hook_name: str, argv: list[str] | None = None) -> int:
    ensure_repo_on_path(repo_root)
    try:
        hooks = importlib.import_module("project_governance.hooks")
    except ModuleNotFoundError as exc:
        if exc.name in {"project_governance", "project_governance.hooks"}:
            return 0
        raise

    hook = getattr(hooks, hook_name, None)
    if not callable(hook):
        return 0

    if argv is None:
        result = hook(repo_root)
    else:
        result = hook(repo_root, argv)
    return 0 if result is None else int(result)
