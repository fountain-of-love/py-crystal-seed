from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

from guardrails_architecture.package_boundaries import check_package_boundaries
from guardrails_architecture.refactoring_guard import check_refactoring_guard
from guardrails_architecture.version_evolution import check_version_evolution
from guardrails_release.release_policy import check_release_policy

from .adr_quality import check_adr_quality
from .docs_drift import check_docs_drift
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


def report_weekly(*, repo_root: Path, output_dir: Path) -> GuardResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
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
    }

    versions = {
        "guardrails-governance": _package_version("guardrails-governance"),
        "guardrails-architecture": _package_version("guardrails-architecture"),
        "guardrails-release": _package_version("guardrails-release"),
        "guardrails-ops": _package_version("guardrails-ops"),
    }

    failing = {name: result for name, result in results.items() if result.status == "fail"}
    warnings = {name: result for name, result in results.items() if result.status == "warn"}
    waivers_result = results["waivers"]
    active_waivers = int(waivers_result.metrics.get("active_waivers", 0))
    expiring_soon = int(waivers_result.metrics.get("expiring_soon", 0))

    payload: dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "package_versions": versions,
        "results": {name: result.to_dict() for name, result in results.items()},
        "summary": {
            "status": "warn" if failing or warnings else "pass",
            "active_waivers": active_waivers,
            "expiring_waivers": expiring_soon,
            "failing_guards": sorted(failing.keys()),
            "warning_guards": sorted(warnings.keys()),
        },
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
    md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return GuardResult(
        guard="weekly_report",
        status="warn" if failing or warnings else "pass",
        metrics={
            "markdown_report": str(md_path),
            "json_report": str(json_path),
            "failing_guards": sorted(failing.keys()),
            "warning_guards": sorted(warnings.keys()),
            "active_waivers": active_waivers,
            "expiring_waivers": expiring_soon,
        },
        advice=["No action required." if not failing and not warnings else "Review findings in the weekly governance report."],
    )
