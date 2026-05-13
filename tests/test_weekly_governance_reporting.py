from __future__ import annotations

import json
from pathlib import Path

from guardrails_governance.weekly_report import report_weekly


ADR_TEXT = (
    "# ADR-0001: Seed\n"
    "- Status: Accepted\n"
    "- Date: 2026-03-01\n"
    "- Decision owners: Platform Team\n\n"
    "## Context\nseed\n\n"
    "## Decision\nseed\n\n"
    "## Alternatives Considered\n1. A\n2. B\n\n"
    "## Consequences\nPositive: Seed\nTradeoff: Seed\n\n"
    "## Validation Evidence\n- pytest\n\n"
    "## Related Docs\n- README.md\n"
)


def _seed_reporting_repo(tmp_path: Path) -> None:
    (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "adr" / "ADR-0001-seed.md").write_text(ADR_TEXT, encoding="utf-8")
    (tmp_path / "waivers").mkdir(parents=True, exist_ok=True)
    (tmp_path / "waivers" / "waivers.yml").write_text("waivers: []\n", encoding="utf-8")
    (tmp_path / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "package_boundaries.yml").write_text("rules: []\n", encoding="utf-8")
    (tmp_path / "tools" / "refactoring_guardrails.yml").write_text(
        "version: 1\ninclude:\n  - src\nignore: []\nrules:\n  ban_wildcard_imports: true\n  max_relative_import_level: 1\n  detect_internal_cycles: false\n  cycle_roots: []\n  directional_dependencies: []\n  forbid_concrete_imports: []\n  composition_roots: []\n  allow_concrete_wiring_only_in: []\n",
        encoding="utf-8",
    )
    (tmp_path / "tools" / "version_evolution_contracts.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "tools" / "coverage_governance.yml").write_text(
        "version: 1\ncoverage_file: coverage.xml\nbaseline_file: tools/coverage_baseline.json\nthresholds:\n  global_min: 80\n  package_min:\n    demo_pkg: 85\nparity:\n  enabled: false\n  max_regression_points: 0.5\nscope:\n  include:\n    - src/**\n  exclude: []\n",
        encoding="utf-8",
    )
    (tmp_path / "tools" / "maturity_evidence.yml").write_text(
        "version: 1\nproduction_paths:\n  - src/**\nexclude_paths:\n  - tests/**\n  - docs/**\nrequired_evidence:\n  any_of:\n    - adr\n    - governance_log\nadr_paths:\n  - docs/adr/**\nroadmap_paths:\n  - docs/maturity/roadmap/**\ngovernance_log: governance/governance_log.yml\nexception_tag: governance-exception\n",
        encoding="utf-8",
    )
    (tmp_path / "tools" / "weekly_reporting.yml").write_text(
        "version: 1\nhistory_dir: artifacts/governance/history\ninclude_guards:\n  - adr_quality\n  - waivers\n  - coverage_governance\n  - maturity_evidence\nretain_reports: 12\nemit_json: true\nemit_markdown: true\n",
        encoding="utf-8",
    )
    (tmp_path / "coverage.xml").write_text("<?xml version=\"1.0\"?><coverage line-rate=\"0.90\"><packages><package name=\"demo_pkg\" line-rate=\"0.88\" /></packages></coverage>", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "demo_pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "governance").mkdir(parents=True, exist_ok=True)
    (tmp_path / "governance" / "governance_log.yml").write_text("version: 1\nentries: []\n", encoding="utf-8")


def test_weekly_reporting_emits_trend_when_history_exists(tmp_path: Path) -> None:
    _seed_reporting_repo(tmp_path)
    output_dir = tmp_path / "artifacts" / "governance"

    first = report_weekly(repo_root=tmp_path, output_dir=output_dir, config_path=tmp_path / "tools" / "weekly_reporting.yml")
    second = report_weekly(repo_root=tmp_path, output_dir=output_dir, config_path=tmp_path / "tools" / "weekly_reporting.yml")

    assert first.exit_code() == 0
    assert second.exit_code() == 0
    payload = json.loads((output_dir / "weekly-report.json").read_text(encoding="utf-8"))
    assert payload["trend"]["history_present"] is True
    assert "coverage_governance" in payload["guard_summaries"]
