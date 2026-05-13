from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(tmp_path: Path) -> str:
    _run(["git", "init"], tmp_path)
    _run(["git", "config", "user.email", "test@example.com"], tmp_path)
    _run(["git", "config", "user.name", "Test User"], tmp_path)
    return "HEAD"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _checker(tmp_path: Path, diff_base: str) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_maturity_evidence.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "DIFF_BASE": diff_base,
        "DIFF_HEAD": "HEAD",
        "MATURITY_EVIDENCE_FILE": str(tmp_path / "tools" / "maturity_evidence.yml"),
    }
    return subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _seed_repo(tmp_path: Path) -> str:
    _init_repo(tmp_path)
    _write(tmp_path / "src" / "demo_pkg" / "__init__.py", "")
    _write(tmp_path / "src" / "demo_pkg" / "service.py", "def run():\n    return 'ok'\n")
    _write(tmp_path / "docs" / "adr" / "ADR-0001-initial.md", "# ADR-0001: Initial\n- Status: Accepted\n- Date: 2026-03-02\n- Decision owners: Platform Team\n\n## Context\nseed\n\n## Decision\nseed\n\n## Alternatives Considered\n1. A\n2. B\n\n## Consequences\nPositive: Seed\nTradeoff: Seed\n\n## Validation Evidence\n- pytest\n\n## Related Docs\n- README.md\n")
    _write(tmp_path / "tools" / "maturity_evidence.yml", "version: 1\nproduction_paths:\n  - src/**\nexclude_paths:\n  - tests/**\n  - docs/**\nrequired_evidence:\n  any_of:\n    - adr\n    - roadmap\n    - governance_log\n    - explicit_exception\nadr_paths:\n  - docs/adr/**\nroadmap_paths:\n  - docs/maturity/roadmap/**\ngovernance_log: governance/governance_log.yml\nexception_tag: governance-exception\n")
    _write(tmp_path / "governance" / "governance_log.yml", "version: 1\nentries: []\n")
    _run(["git", "add", "."], tmp_path)
    _run(["git", "commit", "-m", "seed"], tmp_path)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_maturity_evidence_passes_with_adr_update(tmp_path: Path) -> None:
    base = _seed_repo(tmp_path)
    _write(tmp_path / "src" / "demo_pkg" / "service.py", "def run():\n    return 'better'\n")
    _write(tmp_path / "docs" / "adr" / "ADR-0002-change.md", "# ADR-0002: Change\n- Status: Accepted\n- Date: 2026-03-03\n- Decision owners: Platform Team\n\n## Context\nchange\n\n## Decision\nchange\n\n## Alternatives Considered\n1. A\n2. B\n\n## Consequences\nPositive: Change\nTradeoff: Change\n\n## Validation Evidence\n- pytest\n\n## Related Docs\n- README.md\n")
    _run(["git", "add", "."], tmp_path)

    result = _checker(tmp_path, base)

    assert result.returncode == 0
    assert "evidence=adr" in result.stdout


def test_maturity_evidence_passes_with_governance_log_only(tmp_path: Path) -> None:
    base = _seed_repo(tmp_path)
    _write(tmp_path / "src" / "demo_pkg" / "service.py", "def run():\n    return 'better'\n")
    _write(tmp_path / "governance" / "governance_log.yml", "version: 1\nentries:\n  - id: GOV-0001\n    date: 2026-03-03\n    scope:\n      - src/demo_pkg/service.py\n    evidence:\n      type: governance_log\n      ref: governance/governance_log.yml\n    summary: Govern the production change.\n    owner: Platform Team\n")
    _run(["git", "add", "."], tmp_path)

    result = _checker(tmp_path, base)

    assert result.returncode == 0
    assert "evidence=governance_log" in result.stdout


def test_maturity_evidence_fails_without_evidence(tmp_path: Path) -> None:
    base = _seed_repo(tmp_path)
    _write(tmp_path / "src" / "demo_pkg" / "service.py", "def run():\n    return 'better'\n")
    _run(["git", "add", "."], tmp_path)

    result = _checker(tmp_path, base)

    assert result.returncode == 1
    assert "production changes detected without required governance evidence" in result.stdout
