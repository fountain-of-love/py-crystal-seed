from __future__ import annotations

import os
import re
from pathlib import Path

RE_FILENAME = re.compile(r"^ADR-(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
RE_TITLE = re.compile(r"^# ADR-\d{4}: .+")
RE_STATUS = re.compile(r"^- Status: (Proposed|Accepted|Superseded)$")
RE_DATE = re.compile(r"^- Date: \d{4}-\d{2}-\d{2}$")
RE_OWNERS = re.compile(r"^- Decision owners: .+")

REQUIRED_HEADINGS = [
    "## Context",
    "## Decision",
    "## Alternatives Considered",
    "## Consequences",
    "## Validation Evidence",
    "## Related Docs",
]


def _validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not RE_FILENAME.match(path.name):
        errors.append(f"{path}: invalid filename format")

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        errors.append(f"{path}: file is empty")
        return errors

    if not RE_TITLE.match(lines[0]):
        errors.append(f"{path}: invalid ADR title line")

    body = "\n".join(lines)

    if not any(RE_STATUS.match(line) for line in lines):
        errors.append(f"{path}: missing or invalid status line")
    if not any(RE_DATE.match(line) for line in lines):
        errors.append(f"{path}: missing or invalid date line")
    if not any(RE_OWNERS.match(line) for line in lines):
        errors.append(f"{path}: missing decision owners line")

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"{path}: missing required heading '{heading}'")

    alt_count = sum(1 for line in lines if re.match(r"^\d+\. ", line.strip()))
    if alt_count < 2:
        errors.append(f"{path}: expected at least two numbered alternatives")

    if "Positive:" not in body or "Tradeoff:" not in body:
        errors.append(f"{path}: consequences must include Positive and Tradeoff")

    return errors


def run_adr_quality_check(*, adr_dir: Path) -> int:
    if not adr_dir.exists():
        print("[adr-check] docs/adr not found; skipping")
        return 0

    adrs = sorted(p for p in adr_dir.glob("ADR-*.md") if p.is_file())
    if not adrs:
        print("[adr-check] no ADR files found; skipping")
        return 0

    all_errors: list[str] = []
    for adr in adrs:
        all_errors.extend(_validate_file(adr))

    if all_errors:
        print("[adr-check] validation failed:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"[adr-check] OK: validated {len(adrs)} ADR file(s)")
    return 0


def main() -> int:
    repo_root_env = os.getenv("REPO_ROOT", "").strip()
    repo_root = (
        Path(repo_root_env).resolve() if repo_root_env else Path.cwd()
    )

    adr_dir_env = os.getenv("ADR_DIR", "").strip()
    adr_dir = Path(adr_dir_env).resolve() if adr_dir_env else repo_root / "docs" / "adr"
    return run_adr_quality_check(adr_dir=adr_dir)
