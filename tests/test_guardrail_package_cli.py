from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from guardrails_architecture.cli import check_package_boundaries_cli
from guardrails_governance.cli import check_adr
from guardrails_governance.weekly_report import report_weekly


def test_governance_resources_are_packaged() -> None:
    template = files("guardrails_governance.resources.templates").joinpath("adr_template.md")
    assert template.is_file()
    assert "# ADR-0000" in template.read_text(encoding="utf-8")


def test_architecture_cli_supports_json_output(tmp_path: Path, capsys) -> None:
    src = tmp_path / "src" / "demo_pkg"
    src.mkdir(parents=True, exist_ok=True)
    (src / "__init__.py").write_text("", encoding="utf-8")
    config = tmp_path / "tools" / "package_boundaries.yml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("rules: []\n", encoding="utf-8")

    rc = check_package_boundaries_cli(
        ["--repo-root", str(tmp_path), "--config", str(config), "--output", "json"]
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert '"guard": "package_boundaries"' in out


def test_governance_cli_supports_text_output(tmp_path: Path, capsys) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "ADR-0001-sample.md").write_text(
        "# ADR-0001: Sample Decision\n"
        "- Status: Accepted\n"
        "- Date: 2026-03-01\n"
        "- Decision owners: Platform Team\n\n"
        "## Context\nContext text.\n\n"
        "## Decision\nDecision text.\n\n"
        "## Alternatives Considered\n1. Keep status quo.\n2. Adopt explicit checks.\n\n"
        "## Consequences\nPositive: Better consistency.\nTradeoff: More process overhead.\n\n"
        "## Validation Evidence\n- make governance-check\n\n"
        "## Related Docs\n- docs/maturity/governance-auditability/guardrails-index.md\n",
        encoding="utf-8",
    )

    rc = check_adr(["--repo-root", str(tmp_path), "--output", "text"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "[adr-check] OK: validated 1 ADR file(s)" in out


def test_weekly_report_writes_markdown_and_json(tmp_path: Path) -> None:
    output_dir = tmp_path / "artifacts" / "governance"
    result = report_weekly(repo_root=tmp_path, output_dir=output_dir)

    assert result.exit_code() == 0
    assert (output_dir / "weekly-report.md").exists()
    assert (output_dir / "weekly-report.json").exists()
