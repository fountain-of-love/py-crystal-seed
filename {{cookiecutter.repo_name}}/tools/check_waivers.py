#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_REPO_ROOT))

from tools._guardrail_wrapper import load_cli, resolve_repo_root, run_local_hook

module = load_cli(
    "guardrails_governance.cli",
    SCRIPT_REPO_ROOT / "libs" / "guardrails-governance" / "src",
)

if __name__ == "__main__":
    repo_root = resolve_repo_root()
    config = os.environ.get("WAIVERS_FILE", "").strip() or "waivers/waivers.yml"
    central_rc = int(module.check_waivers(["--repo-root", str(repo_root), "--config", config]))
    if central_rc != 0:
        raise SystemExit(central_rc)
    raise SystemExit(run_local_hook(repo_root, "check_waivers"))
