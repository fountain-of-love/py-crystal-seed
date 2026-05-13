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
    config = os.environ.get("MATURITY_EVIDENCE_FILE", "").strip() or "tools/maturity_evidence.yml"
    argv = ["--repo-root", str(repo_root), "--config", config]
    diff_base = os.environ.get("DIFF_BASE", "").strip()
    diff_head = os.environ.get("DIFF_HEAD", "HEAD").strip()
    if diff_base:
        argv.extend(["--diff-base", diff_base, "--diff-head", diff_head])
    central_rc = int(module.check_maturity_evidence_cli(argv))
    if central_rc != 0:
        raise SystemExit(central_rc)
    raise SystemExit(run_local_hook(repo_root, "check_maturity_evidence"))
