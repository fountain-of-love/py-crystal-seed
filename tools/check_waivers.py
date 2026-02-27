#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

import yaml

REQUIRED_KEYS = {
    "id",
    "control",
    "scope",
    "reason",
    "risk",
    "expires",
    "owner",
    "approvers",
}


def _load_waivers(path: Path) -> list[dict]:
    if not path.exists():
        raise RuntimeError(f"Missing waiver registry: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    waivers = data.get("waivers", [])
    if not isinstance(waivers, list):
        raise RuntimeError("Invalid waivers format: expected top-level list key 'waivers'")
    return waivers


def _validate_entry(entry: dict, today: dt.date) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_KEYS.difference(entry.keys())
    if missing:
        issues.append(f"missing keys: {sorted(missing)}")
        return issues

    if not isinstance(entry["approvers"], list) or not entry["approvers"]:
        issues.append("approvers must be a non-empty list")

    try:
        expires = dt.date.fromisoformat(str(entry["expires"]))
    except ValueError:
        issues.append("expires must be ISO date YYYY-MM-DD")
        return issues

    if expires < today:
        issues.append(f"waiver expired on {expires.isoformat()}")
    return issues


def _write_summary(active: int, expiring_soon: int) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary:
        return
    Path(summary).write_text(
        "\n".join(
            [
                "## Waiver Summary",
                f"- Active waivers: **{active}**",
                f"- Expiring within 14 days: **{expiring_soon}**",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    path = Path("waivers/waivers.yml")
    try:
        waivers = _load_waivers(path)
    except RuntimeError as exc:
        print(f"[waivers] {exc}")
        return 1

    today = dt.date.today()
    violations: list[str] = []
    expiring_soon = 0

    for idx, entry in enumerate(waivers, start=1):
        if not isinstance(entry, dict):
            violations.append(f"entry #{idx}: must be a mapping")
            continue
        issues = _validate_entry(entry, today)
        if issues:
            label = entry.get("id", f"#{idx}")
            for issue in issues:
                violations.append(f"{label}: {issue}")
            continue

        expires = dt.date.fromisoformat(str(entry["expires"]))
        if expires <= today + dt.timedelta(days=14):
            expiring_soon += 1

    if violations:
        print("[waivers] Violations:")
        for item in violations:
            print(f"  - {item}")
        return 1

    print(f"[waivers] OK (active waivers: {len(waivers)}, expiring soon: {expiring_soon})")
    _write_summary(active=len(waivers), expiring_soon=expiring_soon)
    return 0


if __name__ == "__main__":
    sys.exit(main())
