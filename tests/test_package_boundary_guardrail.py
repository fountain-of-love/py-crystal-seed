from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_checker(tmp_path: Path, config: Path) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_package_boundaries.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "PACKAGE_BOUNDARIES_FILE": str(config),
    }
    return subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_package_boundary_guardrail_detects_forbidden_cross_import(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"

    _write(src / "runtime" / "__init__.py", "")
    _write(src / "runtime" / "service.py", "from demo_pkg.research.helper import plan\n")
    _write(src / "research" / "__init__.py", "")
    _write(src / "research" / "helper.py", "def plan():\n    return 'ok'\n")

    config = tmp_path / "boundaries.yml"
    config.write_text(
        "rules:\n"
        "  - package: demo_pkg.runtime\n"
        "    forbidden_prefixes:\n"
        "      - demo_pkg.research\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "Violations found" in result.stdout
    assert "demo_pkg.research.helper" in result.stdout


def test_package_boundary_guardrail_passes_when_imports_respect_rules(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"

    _write(src / "runtime" / "__init__.py", "")
    _write(src / "runtime" / "service.py", "from demo_pkg.runtime.adapters import run\n")
    _write(src / "runtime" / "adapters.py", "def run():\n    return 'ok'\n")

    config = tmp_path / "boundaries.yml"
    config.write_text(
        "rules:\n"
        "  - package: demo_pkg.runtime\n"
        "    forbidden_prefixes:\n"
        "      - demo_pkg.research\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 0
    assert "OK: no forbidden cross-package imports detected." in result.stdout
