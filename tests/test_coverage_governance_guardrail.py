from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from guardrails_governance.coverage_governance import check_coverage_governance


COVERAGE_XML = """<?xml version=\"1.0\" ?>
<coverage line-rate=\"0.90\">
  <packages>
    <package name=\"py_crystal_seed\" line-rate=\"0.88\" />
  </packages>
</coverage>
"""


def _run_checker(tmp_path: Path, config: Path) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_coverage_governance.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "COVERAGE_GOVERNANCE_FILE": str(config),
    }
    return subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_coverage_governance_passes_thresholds_and_parity(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML, encoding="utf-8")
    (tmp_path / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "coverage_baseline.json").write_text(
        json.dumps({"global_coverage": 90.2}), encoding="utf-8"
    )
    config = tmp_path / "coverage.yml"
    config.write_text(
        "version: 1\n"
        "coverage_file: coverage.xml\n"
        "baseline_file: tools/coverage_baseline.json\n"
        "thresholds:\n"
        "  global_min: 80\n"
        "  package_min:\n"
        "    py_crystal_seed: 85\n"
        "parity:\n"
        "  enabled: true\n"
        "  max_regression_points: 0.5\n"
        "scope:\n"
        "  include:\n"
        "    - src/**\n"
        "  exclude:\n"
        "    - tests/**\n",
        encoding="utf-8",
    )

    result = check_coverage_governance(repo_root=tmp_path, config_path=config)

    assert result.exit_code() == 0
    assert result.metrics["global_coverage"] == 90.0


def test_coverage_governance_fails_for_missing_coverage_xml(tmp_path: Path) -> None:
    config = tmp_path / "coverage.yml"
    config.write_text(
        "version: 1\n"
        "coverage_file: coverage.xml\n"
        "baseline_file: tools/coverage_baseline.json\n"
        "thresholds:\n"
        "  global_min: 80\n"
        "  package_min: {}\n"
        "parity:\n"
        "  enabled: false\n"
        "  max_regression_points: 0.5\n"
        "scope:\n"
        "  include:\n"
        "    - src/**\n"
        "  exclude: []\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "coverage file not found" in result.stdout


def test_coverage_governance_fails_for_regression(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML, encoding="utf-8")
    (tmp_path / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "coverage_baseline.json").write_text(
        json.dumps({"global_coverage": 91.0}), encoding="utf-8"
    )
    config = tmp_path / "coverage.yml"
    config.write_text(
        "version: 1\n"
        "coverage_file: coverage.xml\n"
        "baseline_file: tools/coverage_baseline.json\n"
        "thresholds:\n"
        "  global_min: 80\n"
        "  package_min:\n"
        "    py_crystal_seed: 85\n"
        "parity:\n"
        "  enabled: true\n"
        "  max_regression_points: 0.5\n"
        "scope:\n"
        "  include:\n"
        "    - src/**\n"
        "  exclude: []\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "coverage regression exceeds allowed maximum" in result.stdout
