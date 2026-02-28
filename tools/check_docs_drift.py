#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REQUIRED_DOCS = {
    "README.md",
    "DEVELOPER_README.md",
    "ENGINEERING_PRACTICES.md",
    "PR_REVIEW_CHECKLIST.md",
    "RELEASING.md",
    "docs/README.md",
    "docs/ci-pipeline.md",
    "docs/packaging-distribution.md",
    "scripts/README.md",
    "tools/README.md",
    "dev-ops/README.md",
}

DRIFT_RULES = [
    {
        "trigger_prefixes": ("scripts/",),
        "required_any": ("scripts/README.md", "dev-ops/README.md", "README.md"),
        "message": "Scripts changed but no script/workflow docs were updated.",
    },
    {
        "trigger_prefixes": (".github/workflows/",),
        "required_any": ("docs/ci-pipeline.md", "docs/packaging-distribution.md", "README.md"),
        "message": "CI workflows changed but CI/packaging docs were not updated.",
    },
    {
        "trigger_prefixes": (".gitlab-ci.yml",),
        "required_any": ("docs/ci-pipeline.md", "docs/packaging-distribution.md", "README.md"),
        "message": "GitLab CI changed but CI/packaging docs were not updated.",
    },
    {
        "trigger_prefixes": ("tools/",),
        "required_any": ("tools/README.md", "DEVELOPER_README.md"),
        "message": "Tools changed but tool/developer docs were not updated.",
    },
    {
        "trigger_prefixes": ("pyproject.toml",),
        "required_any": ("README.md", "dev-ops/README.md", "docs/packaging-distribution.md"),
        "message": "Packaging/project metadata changed but docs were not updated.",
    },
]


def _changed_files(diff_base: str, diff_head: str) -> set[str]:
    cmd = ["git", "diff", "--name-only", f"{diff_base}...{diff_head}"]
    out = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "git diff failed")
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def _exists_check() -> list[str]:
    missing = []
    for file_path in sorted(REQUIRED_DOCS):
        if not Path(file_path).exists():
            missing.append(file_path)
    return missing


def _violations_for_changed(changed: set[str]) -> list[str]:
    violations: list[str] = []
    if not changed:
        return violations

    for rule in DRIFT_RULES:
        triggered = any(
            any(path == prefix or path.startswith(prefix) for prefix in rule["trigger_prefixes"])
            for path in changed
        )
        if not triggered:
            continue
        if not any(doc in changed for doc in rule["required_any"]):
            violations.append(rule["message"])
    return violations


def main() -> int:
    missing = _exists_check()
    if missing:
        print("[docs-drift] Missing required docs:")
        for item in missing:
            print(f"  - {item}")
        return 1

    diff_base = os.environ.get("DIFF_BASE", "").strip()
    diff_head = os.environ.get("DIFF_HEAD", "HEAD").strip()
    if not diff_base:
        print("[docs-drift] Presence checks passed (no DIFF_BASE provided; drift checks skipped).")
        return 0

    try:
        changed = _changed_files(diff_base=diff_base, diff_head=diff_head)
    except RuntimeError as exc:
        print(f"[docs-drift] Unable to evaluate change-aware drift rules: {exc}")
        return 1

    violations = _violations_for_changed(changed)
    if violations:
        print("[docs-drift] Violations:")
        for item in violations:
            print(f"  - {item}")
        print("[docs-drift] Update docs in the same PR or adjust policy intentionally.")
        return 1

    print("[docs-drift] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
