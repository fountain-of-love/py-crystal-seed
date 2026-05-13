from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, cast

import yaml

from .result import GuardResult


class MaturityEvidenceConfig(dict[str, Any]):
    pass


def _load_config(config_path: Path) -> MaturityEvidenceConfig:
    if not config_path.exists():
        raise RuntimeError(f"maturity evidence config not found: {config_path}")

    payload_obj: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("maturity evidence config must be a mapping")
    payload = cast(dict[str, Any], payload_obj)

    version = payload.get("version")
    if version != 1:
        raise RuntimeError("maturity evidence config version must be 1")

    def _string_list(key: str, default: list[str]) -> list[str]:
        value = payload.get(key, default)
        if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
            raise RuntimeError(f"{key} must be a list of non-empty strings")
        return cast(list[str], value)

    required_evidence_obj = payload.get("required_evidence", {})
    if not isinstance(required_evidence_obj, dict):
        raise RuntimeError("required_evidence must be a mapping")
    any_of = required_evidence_obj.get("any_of", [])
    if not isinstance(any_of, list) or not all(isinstance(x, str) and x for x in any_of):
        raise RuntimeError("required_evidence.any_of must be a list of non-empty strings")

    governance_log = payload.get("governance_log", "governance/governance_log.yml")
    exception_tag = payload.get("exception_tag", "governance-exception")
    if not isinstance(governance_log, str) or not governance_log.strip():
        raise RuntimeError("governance_log must be a non-empty string")
    if not isinstance(exception_tag, str) or not exception_tag.strip():
        raise RuntimeError("exception_tag must be a non-empty string")

    return MaturityEvidenceConfig(
        {
            "version": 1,
            "production_paths": _string_list("production_paths", ["src/**"]),
            "exclude_paths": _string_list("exclude_paths", ["tests/**", "docs/**"]),
            "required_evidence": {"any_of": cast(list[str], any_of)},
            "adr_paths": _string_list("adr_paths", ["docs/adr/**"]),
            "roadmap_paths": _string_list("roadmap_paths", ["docs/maturity/roadmap/**"]),
            "governance_log": governance_log.strip(),
            "exception_tag": exception_tag.strip(),
        }
    )


def _git_changed(repo_root: Path, diff_base: str, diff_head: str) -> set[str]:
    changed: set[str] = set()

    def _collect(cmd: list[str]) -> None:
        out = subprocess.run(cmd, cwd=repo_root, check=False, capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(out.stderr.strip() or "git diff failed")
        changed.update(line.strip() for line in out.stdout.splitlines() if line.strip())

    _collect(["git", "diff", "--name-only", f"{diff_base}...{diff_head}"])
    if diff_head == "HEAD":
        _collect(["git", "diff", "--name-only", "--cached"])
        _collect(["git", "diff", "--name-only"])
    return changed


def _matches_any(path: str, patterns: list[str]) -> bool:
    path_obj = Path(path)
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if path == prefix or path.startswith(f"{prefix}/"):
                return True
        if path_obj.match(pattern):
            return True
    return False


def _load_governance_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"governance log not found: {path}")
    payload_obj: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("governance log must be a mapping")
    payload = cast(dict[str, Any], payload_obj)
    if payload.get("version") != 1:
        raise RuntimeError("governance log version must be 1")
    entries_obj = payload.get("entries", [])
    if not isinstance(entries_obj, list):
        raise RuntimeError("governance log entries must be a list")
    entries: list[dict[str, Any]] = []
    for entry in entries_obj:
        if not isinstance(entry, dict):
            raise RuntimeError("governance log entries must be mappings")
        entries.append(cast(dict[str, Any], entry))
    return entries


def _validate_log_entry(entry: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = ["id", "date", "scope", "evidence", "summary", "owner"]
    for key in required:
        if key not in entry:
            issues.append(f"missing key '{key}'")
    if issues:
        return issues

    scope = entry.get("scope")
    if not isinstance(scope, list) or not all(isinstance(x, str) and x for x in scope):
        issues.append("scope must be a non-empty list of strings")

    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        issues.append("evidence must be a mapping")
    else:
        if not isinstance(evidence.get("type"), str) or not str(evidence.get("type")).strip():
            issues.append("evidence.type must be a non-empty string")
        if not isinstance(evidence.get("ref"), str) or not str(evidence.get("ref")).strip():
            issues.append("evidence.ref must be a non-empty string")

    if not isinstance(entry.get("summary"), str) or not str(entry.get("summary")).strip():
        issues.append("summary must be a non-empty string")
    if not isinstance(entry.get("owner"), str) or not str(entry.get("owner")).strip():
        issues.append("owner must be a non-empty string")
    return issues


def check_maturity_evidence(
    *,
    repo_root: Path,
    config_path: Path,
    diff_base: str,
    diff_head: str,
) -> GuardResult:
    try:
        config = _load_config(config_path)
    except RuntimeError as exc:
        return GuardResult(
            guard="maturity_evidence",
            status="fail",
            violations=[{"message": str(exc)}],
        )

    if not diff_base:
        return GuardResult(
            guard="maturity_evidence",
            status="pass",
            metrics={"skipped": True, "reason": "no diff base provided"},
            advice=["No diff base provided; maturity evidence check skipped."],
        )

    try:
        changed = _git_changed(repo_root, diff_base, diff_head)
    except RuntimeError as exc:
        return GuardResult(
            guard="maturity_evidence",
            status="fail",
            violations=[{"message": f"unable to evaluate changed files: {exc}"}],
        )

    production_paths = cast(list[str], config["production_paths"])
    exclude_paths = cast(list[str], config["exclude_paths"])
    changed_production = sorted(
        path
        for path in changed
        if _matches_any(path, production_paths) and not _matches_any(path, exclude_paths)
    )
    if not changed_production:
        return GuardResult(
            guard="maturity_evidence",
            status="pass",
            metrics={"skipped": True, "changed_production": []},
            advice=["No production changes detected; maturity evidence check skipped."],
        )

    violations: list[str] = []
    evidence_found: list[str] = []
    required_any = cast(list[str], cast(dict[str, Any], config["required_evidence"])["any_of"])
    adr_paths = cast(list[str], config["adr_paths"])
    roadmap_paths = cast(list[str], config["roadmap_paths"])
    exception_tag = cast(str, config["exception_tag"])

    if "adr" in required_any and any(_matches_any(path, adr_paths) for path in changed):
        evidence_found.append("adr")

    if "roadmap" in required_any and any(_matches_any(path, roadmap_paths) for path in changed):
        evidence_found.append("roadmap")

    governance_log_path = repo_root / cast(str, config["governance_log"])
    if "governance_log" in required_any:
        try:
            entries = _load_governance_log(governance_log_path)
        except RuntimeError as exc:
            if not evidence_found:
                violations.append(str(exc))
            entries = []
        valid_log_cover = False
        for entry in entries:
            entry_issues = _validate_log_entry(entry)
            if entry_issues:
                label = str(entry.get("id", "unknown"))
                if not evidence_found:
                    violations.extend(f"governance log entry {label}: {issue}" for issue in entry_issues)
                continue
            scope = cast(list[str], entry["scope"])
            if any(item in changed_production for item in scope):
                valid_log_cover = True
        if valid_log_cover:
            evidence_found.append("governance_log")
        elif governance_log_path.exists() and not evidence_found and not violations:
            violations.append("governance log does not cover the changed production scope")

    if "explicit_exception" in required_any and any(exception_tag in path for path in changed):
        evidence_found.append("explicit_exception")

    if not evidence_found:
        violations.append(
            "production changes detected without required governance evidence "
            f"(accepted: {', '.join(required_any)})"
        )

    return GuardResult(
        guard="maturity_evidence",
        status="fail" if violations else "pass",
        violations=[{"message": item} for item in violations],
        metrics={
            "changed_production": changed_production,
            "evidence_found": evidence_found,
            "diff_base": diff_base,
            "diff_head": diff_head,
        },
    )


def format_maturity_evidence_result(result: GuardResult) -> str:
    if result.metrics.get("skipped"):
        return f"[maturity-evidence] {result.advice[0]}"
    if result.status == "fail":
        lines = ["[maturity-evidence] Violations:"]
        lines.extend(f"  - {item['message']}" for item in result.violations)
        return "\n".join(lines)
    changed = cast(list[str], result.metrics.get("changed_production", []))
    evidence = cast(list[str], result.metrics.get("evidence_found", []))
    return (
        "[maturity-evidence] OK "
        f"(changed_production={len(changed)}, evidence={','.join(evidence)})"
    )


def run_maturity_evidence_check(
    *,
    repo_root: Path,
    config_path: Path,
    diff_base: str,
    diff_head: str,
) -> int:
    result = check_maturity_evidence(
        repo_root=repo_root,
        config_path=config_path,
        diff_base=diff_base,
        diff_head=diff_head,
    )
    print(format_maturity_evidence_result(result))
    return result.exit_code()
