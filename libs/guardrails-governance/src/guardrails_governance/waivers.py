from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Any, cast

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


def _load_waivers(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"Missing waiver registry: {path}")
    raw_payload: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload_obj: Any = raw_payload or {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("Invalid waivers format: expected mapping")
    payload = cast(dict[str, Any], payload_obj)
    waivers_obj = payload.get("waivers", [])
    if not isinstance(waivers_obj, list):
        raise RuntimeError("Invalid waivers format: expected top-level list key 'waivers'")
    waivers = cast(list[Any], waivers_obj)
    normalized: list[dict[str, Any]] = []
    for entry in waivers:
        if not isinstance(entry, dict):
            normalized.append({"_invalid_entry": entry})
            continue
        normalized.append(cast(dict[str, Any], entry))
    return normalized


def _validate_entry(entry: dict[str, Any], today: dt.date) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_KEYS.difference(entry.keys())
    if missing:
        issues.append(f"missing keys: {sorted(missing)}")
        return issues

    approvers = entry["approvers"]
    if not isinstance(approvers, list) or not approvers:
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


def run_waiver_check(*, waiver_file: Path, today: dt.date | None = None) -> int:
    try:
        waivers = _load_waivers(waiver_file)
    except RuntimeError as exc:
        print(f"[waivers] {exc}")
        return 1

    current_day = today or dt.date.today()
    violations: list[str] = []
    expiring_soon = 0

    for idx, entry in enumerate(waivers, start=1):
        if "_invalid_entry" in entry:
            violations.append(f"entry #{idx}: must be a mapping")
            continue
        issues = _validate_entry(entry, current_day)
        if issues:
            label = str(entry.get("id", f"#{idx}"))
            for issue in issues:
                violations.append(f"{label}: {issue}")
            continue

        expires = dt.date.fromisoformat(str(entry["expires"]))
        if expires <= current_day + dt.timedelta(days=14):
            expiring_soon += 1

    if violations:
        print("[waivers] Violations:")
        for item in violations:
            print(f"  - {item}")
        return 1

    print(f"[waivers] OK (active waivers: {len(waivers)}, expiring soon: {expiring_soon})")
    _write_summary(active=len(waivers), expiring_soon=expiring_soon)
    return 0


def main() -> int:
    repo_root_env = os.environ.get("REPO_ROOT", "").strip()
    repo_root = Path(repo_root_env).resolve() if repo_root_env else Path.cwd()
    return run_waiver_check(waiver_file=repo_root / "waivers" / "waivers.yml")
