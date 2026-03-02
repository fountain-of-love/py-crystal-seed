#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _load_module() -> object:
    module_name = "guardrails_architecture.version_evolution"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        local_src = REPO_ROOT / "libs" / "guardrails-architecture" / "src"
        if local_src.exists() and str(local_src) not in sys.path:
            sys.path.insert(0, str(local_src))
        return importlib.import_module(module_name)


module = _load_module()

if __name__ == "__main__":
    raise SystemExit(module.main(sys.argv[1:]))
