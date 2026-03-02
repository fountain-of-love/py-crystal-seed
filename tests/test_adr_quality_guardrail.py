from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_checker(adr_dir: Path) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_adr_quality.py"
    env = {
        **os.environ,
        "ADR_DIR": str(adr_dir),
    }
    return subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_adr_quality_guardrail_fails_for_missing_required_sections(tmp_path: Path) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    (adr_dir / "ADR-0001-sample.md").write_text(
        "# ADR-0001: Sample Decision\n"
        "- Status: Accepted\n"
        "- Date: 2026-03-01\n"
        "- Decision owners: Platform Team\n\n"
        "## Context\n"
        "Context text.\n\n"
        "## Decision\n"
        "Decision text.\n",
        encoding="utf-8",
    )

    result = _run_checker(adr_dir)

    assert result.returncode == 1
    assert "missing required heading '## Alternatives Considered'" in result.stdout


def test_adr_quality_guardrail_passes_for_valid_template(tmp_path: Path) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    (adr_dir / "ADR-0001-sample.md").write_text(
        "# ADR-0001: Sample Decision\n"
        "- Status: Accepted\n"
        "- Date: 2026-03-01\n"
        "- Decision owners: Platform Team\n\n"
        "## Context\n"
        "Context text.\n\n"
        "## Decision\n"
        "Decision text.\n\n"
        "## Alternatives Considered\n"
        "1. Keep status quo.\n"
        "2. Adopt explicit guardrail checks.\n\n"
        "## Consequences\n"
        "Positive: Better consistency.\n"
        "Tradeoff: More process overhead.\n\n"
        "## Validation Evidence\n"
        "- make governance-check\n\n"
        "## Related Docs\n"
        "- docs/maturity/governance-auditability/guardrails-index.md\n",
        encoding="utf-8",
    )

    result = _run_checker(adr_dir)

    assert result.returncode == 0
    assert "OK: validated 1 ADR file(s)" in result.stdout
