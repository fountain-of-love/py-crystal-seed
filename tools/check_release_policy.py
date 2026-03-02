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
    "guardrails_release.cli",
    SCRIPT_REPO_ROOT / "libs" / "guardrails-release" / "src",
)

if __name__ == "__main__":
    repo_root = resolve_repo_root()
    argv = ["--repo-root", str(repo_root)]
    release_tag = os.environ.get("RELEASE_TAG", "").strip()
    diff_base = os.environ.get("DIFF_BASE", "").strip()
    diff_head = os.environ.get("DIFF_HEAD", "HEAD").strip()
    if release_tag:
        argv.extend(["--release-tag", release_tag])
    if diff_base:
        argv.extend(["--diff-base", diff_base, "--diff-head", diff_head])
    central_rc = int(module.check_release_policy(argv))
    if central_rc != 0:
        raise SystemExit(central_rc)
    raise SystemExit(run_local_hook(repo_root, "check_release_policy"))
