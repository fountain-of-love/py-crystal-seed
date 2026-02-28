from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_checker(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_version_import_boundaries.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "ROOT_PACKAGE": "demo_pkg",
        "VERSION_NAMESPACE": "versions",
        "CORE_NAMESPACE": "core",
    }
    return subprocess.run(
        [sys.executable, str(checker), *extra_args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_guardrail_detects_core_contract_drift_for_lower_version_usage(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"

    _write(src / "__init__.py", "")
    _write(src / "core" / "__init__.py", "")
    _write(src / "core" / "api.py", "def make_run(name):\n    return name\n")

    _write(src / "versions" / "__init__.py", "")
    _write(src / "versions" / "v1" / "__init__.py", "")
    _write(src / "versions" / "v1" / "facade.py", "class V1Facade:\n    pass\n")
    _write(src / "versions" / "v1" / "worker.py", "from demo_pkg.core.api import make_run\n")

    _write(src / "versions" / "v2" / "__init__.py", "")
    _write(
        src / "versions" / "v2" / "worker.py",
        "from demo_pkg.versions.v1 import facade\n",
    )

    # Baseline contract generation.
    write_result = _run_checker(tmp_path, "--write-contract")
    assert write_result.returncode == 0

    # Drift: changing a protected core contract signature.
    _write(src / "core" / "api.py", "def make_run(name, status):\n    return f'{name}:{status}'\n")
    result = _run_checker(tmp_path)
    assert result.returncode == 1
    assert "[compatibility] Violations found:" in result.stdout
    assert "contract drift for api::make_run" in result.stdout
