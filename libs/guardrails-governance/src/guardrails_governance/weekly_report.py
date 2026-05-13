from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, cast

import yaml
from guardrails_architecture.package_boundaries import check_package_boundaries
from guardrails_architecture.refactoring_guard import check_refactoring_guard
from guardrails_architecture.version_evolution import check_version_evolution
from guardrails_release.release_policy import check_release_policy

from .adr_quality import check_adr_quality
from .coverage_governance import check_coverage_governance
from .docs_drift import check_docs_drift
from .maturity_evidence import check_maturity_evidence
from .result import GuardResult
from .waivers import check_waivers


def _discover_root_package(src_root: Path) -> str:
    if not src_root.exists():
        return ""
    packages = [
        child.name
        for child in src_root.iterdir()
        if child.is_dir()
        and (child / "__init__.py").exists()
        and not child.name.startswith("guardrails_")
    ]
    return packages[0] if len(packages) == 1 else ""


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "local-editable"


def _load_reporting_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "version": 1,
            "history_dir": "artifacts/governance/history",
            "include_guards": [
                "docs_drift",
                "waivers",
                "release_policy",
                "version_evolution",
                "package_boundaries",
                "refactoring_guard",
                "adr_quality",
                "coverage_governance",
                "maturity_evidence",
            ],
            "retain_reports": 12,
            "emit_json": True,
            "emit_markdown": True,
        }
    payload_obj: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("weekly reporting config must be a mapping")
    payload = cast(dict[str, Any], payload_obj)
    if payload.get("version") != 1:
        raise RuntimeError("weekly reporting config version must be 1")
    include_guards = payload.get("include_guards", [])
    if not isinstance(include_guards, list) or not all(isinstance(x, str) for x in include_guards):
        raise RuntimeError("include_guards must be a list of strings")
    return {
        "version": 1,
        "history_dir": str(payload.get("history_dir", "artifacts/governance/history")),
        "include_guards": cast(list[str], include_guards),
        "retain_reports": int(payload.get("retain_reports", 12)),
        "emit_json": bool(payload.get("emit_json", True)),
        "emit_markdown": bool(payload.get("emit_markdown", True)),
    }


def _history_payloads(history_dir: Path, retain_reports: int) -> list[dict[str, Any]]:
    if not history_dir.exists():
        return []
    payloads: list[dict[str, Any]] = []
    for path in sorted(history_dir.glob("weekly-report-*.json"))[-retain_reports:]:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            payloads.append(cast(dict[str, Any], obj))
    return payloads


def _guard_status_payload(result: GuardResult) -> dict[str, Any]:
    return {
        "guard": result.guard,
        "status": result.status,
        "metrics": result.metrics,
        "violations": result.violations,
        "warnings": result.warnings,
        "advice": result.advice,
    }


def _trend(current: dict[str, GuardResult], history: list[dict[str, Any]]) -> dict[str, Any]:
    if not history:
        return {"history_present": False}
    previous = history[-1]
    previous_results = cast(dict[str, Any], previous.get("guard_summaries", {}))
    trend: dict[str, Any] = {"history_present": True, "guards": {}}
    for name, result in current.items():
        prev_guard = cast(dict[str, Any], previous_results.get(name, {}))
        prev_status = str(prev_guard.get("status", "unknown"))
        prev_metrics = cast(dict[str, Any], prev_guard.get("metrics", {}))
        current_metrics = result.metrics
        entry: dict[str, Any] = {
            "previous_status": prev_status,
            "status_changed": prev_status not in {"", "unknown"} and prev_status != result.status,
        }
        if name == "waivers":
            entry["active_delta"] = int(current_metrics.get("active_waivers", 0)) - int(prev_metrics.get("active_waivers", 0))
            entry["expiring_delta"] = int(current_metrics.get("expiring_soon", 0)) - int(prev_metrics.get("expiring_soon", 0))
        if name == "coverage_governance":
            prev_global = prev_metrics.get("global_coverage")
            current_global = current_metrics.get("global_coverage")
            if isinstance(prev_global, (int, float)) and isinstance(current_global, (int, float)):
                entry["global_coverage_delta"] = round(float(current_global) - float(prev_global), 2)
        trend["guards"][name] = entry
    return trend


def report_weekly(*, repo_root: Path, output_dir: Path, config_path: Path | None = None, history_dir: Path | None = None) -> GuardResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = _load_reporting_config(config_path or (repo_root / "tools" / "weekly_reporting.yml"))
    resolved_history_dir = history_dir or (repo_root / cast(str, config["history_dir"]))
    resolved_history_dir.mkdir(parents=True, exist_ok=True)

    all_results = {
        "adr_quality": check_adr_quality(adr_dir=repo_root / "docs" / "adr"),
        "docs_drift": check_docs_drift(repo_root=repo_root, diff_base="", diff_head="HEAD"),
        "waivers": check_waivers(waiver_file=repo_root / "waivers" / "waivers.yml"),
        "package_boundaries": check_package_boundaries(
            repo_root=repo_root,
            config_path=(repo_root / "tools" / "package_boundaries.yml").resolve(),
        ),
        "refactoring_guard": check_refactoring_guard(
            repo_root=repo_root,
            config_path=(repo_root / "tools" / "refactoring_guardrails.yml").resolve(),
        ),
        "version_evolution": check_version_evolution(
            repo_root=repo_root,
            root_package=_discover_root_package(repo_root / "src"),
            version_namespace="versions",
            core_namespace="core",
            contracts_file=(repo_root / "tools" / "version_evolution_contracts.json").resolve(),
            write_contract=False,
        ),
        "release_policy": check_release_policy(
            repo_root=repo_root,
            release_tag="",
            diff_base="",
            diff_head="HEAD",
        ),
        "coverage_governance": check_coverage_governance(
            repo_root=repo_root,
            config_path=(repo_root / "tools" / "coverage_governance.yml").resolve(),
        ),
        "maturity_evidence": check_maturity_evidence(
            repo_root=repo_root,
            config_path=(repo_root / "tools" / "maturity_evidence.yml").resolve(),
            diff_base="",
            diff_head="HEAD",
        ),
    }

    include_guards = cast(list[str], config["include_guards"])
    results = {name: result for name, result in all_results.items() if name in include_guards}

    versions = {
        "guardrails-governance": _package_version("guardrails-governance"),
        "guardrails-architecture": _package_version("guardrails-architecture"),
        "guardrails-release": _package_version("guardrails-release"),
        "guardrails-ops": _package_version("guardrails-ops"),
    }

    failing = {name: result for name, result in results.items() if result.status == "fail"}
    warnings = {name: result for name, result in results.items() if result.status == "warn"}
    waivers_result = results.get("waivers", GuardResult(guard="waivers", status="pass"))
    active_waivers = int(waivers_result.metrics.get("active_waivers", 0))
    expiring_soon = int(waivers_result.metrics.get("expiring_soon", 0))

    history = _history_payloads(resolved_history_dir, int(config["retain_reports"]))
    trend = _trend(results, history)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "guard_versions": versions,
        "guard_summaries": {name: _guard_status_payload(result) for name, result in results.items()},
        "trend": trend,
        "summary": {
            "status": "warn" if failing or warnings else "pass",
            "active_waivers": active_waivers,
            "expiring_waivers": expiring_soon,
            "failing_guards": sorted(failing.keys()),
            "warning_guards": sorted(warnings.keys()),
        },
        "advice": [
            "No action required." if not failing and not warnings else "Review findings in the weekly governance report."
        ],
    }

    markdown_lines = [
        "# Weekly Governance Report",
        f"- Generated at: {payload['generated_at']}",
        f"- Repo root: `{repo_root}`",
        "",
        "## Package Versions",
    ]
    markdown_lines.extend(f"- `{name}`: `{version}`" for name, version in versions.items())
    markdown_lines.extend(
        [
            "",
            "## Guard Summary",
            f"- Active waivers: **{active_waivers}**",
            f"- Expiring waivers: **{expiring_soon}**",
        ]
    )
    for name, result in results.items():
        markdown_lines.append(f"- `{name}`: **{result.status}**")
    markdown_lines.append("")

    markdown_lines.append("## Trend")
    if not trend.get("history_present"):
        markdown_lines.append("- No prior weekly history available yet.")
    else:
        for name, entry in cast(dict[str, Any], trend.get("guards", {})).items():
            markdown_lines.append(
                f"- `{name}`: previous=`{entry.get('previous_status', 'unknown')}`, changed=`{entry.get('status_changed', False)}`"
            )
            if "active_delta" in entry:
                markdown_lines.append(
                    f"  waivers delta: active={entry['active_delta']}, expiring={entry['expiring_delta']}"
                )
            if "global_coverage_delta" in entry:
                markdown_lines.append(
                    f"  coverage delta: {entry['global_coverage_delta']} points"
                )
    markdown_lines.append("")

    if failing or warnings:
        markdown_lines.append("## Findings")
        for name, result in results.items():
            if result.status == "pass":
                continue
            markdown_lines.append(f"### {name}")
            for item in result.violations:
                markdown_lines.append(f"- {item.get('message', '')}")
            for item in result.warnings:
                markdown_lines.append(f"- Warning: {item.get('message', '')}")
            for advice in result.advice:
                markdown_lines.append(f"- Advice: {advice}")
    else:
        markdown_lines.extend(["## No Action Required", "- All configured governance checks passed."])

    md_path = output_dir / "weekly-report.md"
    json_path = output_dir / "weekly-report.json"
    history_snapshot = resolved_history_dir / f"weekly-report-{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"

    if bool(config["emit_markdown"]):
        md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    if bool(config["emit_json"]):
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        history_snapshot.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return GuardResult(
        guard="weekly_report",
        status="warn" if failing or warnings else "pass",
        metrics={
            "markdown_report": str(md_path),
            "json_report": str(json_path),
            "history_snapshot": str(history_snapshot),
            "failing_guards": sorted(failing.keys()),
            "warning_guards": sorted(warnings.keys()),
            "active_waivers": active_waivers,
            "expiring_waivers": expiring_soon,
        },
        advice=[payload["advice"][0]],
    )
