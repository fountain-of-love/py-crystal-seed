from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_checker(tmp_path: Path, config: Path) -> subprocess.CompletedProcess[str]:
    checker = Path(__file__).resolve().parents[1] / "tools" / "check_refactoring_guard.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "REFACTORING_GUARD_FILE": str(config),
    }
    return subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_refactoring_guardrail_fails_on_wildcard_import(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "__init__.py", "")
    _write(src / "helpers.py", "value = 1\n")
    _write(src / "service.py", "from demo_pkg.helpers import *\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 1\n"
        "  detect_internal_cycles: false\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "wildcard imports are forbidden" in result.stdout


def test_refactoring_guardrail_fails_on_upward_relative_import(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "__init__.py", "")
    _write(src / "shared.py", "value = 1\n")
    _write(src / "feature" / "__init__.py", "")
    _write(src / "feature" / "service.py", "from ..shared import value\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 0\n"
        "  detect_internal_cycles: false\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "relative import level 2 exceeds allowed maximum 0" in result.stdout


def test_refactoring_guardrail_fails_on_internal_cycle(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "__init__.py", "")
    _write(src / "a.py", "from demo_pkg.b import run_b\n")
    _write(src / "b.py", "from demo_pkg.a import run_a\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 1\n"
        "  detect_internal_cycles: true\n"
        "  cycle_roots:\n"
        "    - demo_pkg\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "internal dependency cycle detected" in result.stdout


def test_refactoring_guardrail_passes_for_clean_structure(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "__init__.py", "")
    _write(src / "main.py", "def greet():\n    return 'ok'\n")
    _write(src / "api" / "__init__.py", "")
    _write(src / "api" / "service.py", "from demo_pkg.main import greet\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 1\n"
        "  detect_internal_cycles: true\n"
        "  cycle_roots:\n"
        "    - demo_pkg\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 0
    assert "OK: no structural refactoring violations detected." in result.stdout


def test_refactoring_guardrail_fails_on_wrong_dependency_direction(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "presentation" / "__init__.py", "")
    _write(src / "business" / "__init__.py", "")
    _write(src / "business" / "service.py", "def run():\n    return 'ok'\n")
    _write(src / "presentation" / "page.py", "from demo_pkg.business.service import run\n")
    _write(src / "business" / "rule.py", "from demo_pkg.presentation.page import run\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "version: 1\n"
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 1\n"
        "  detect_internal_cycles: false\n"
        "  cycle_roots: []\n"
        "  directional_dependencies:\n"
        "    - from: demo_pkg.presentation\n"
        "      may_import:\n"
        "        - demo_pkg.business\n"
        "    - from: demo_pkg.business\n"
        "      may_import: []\n"
        "  forbid_concrete_imports: []\n"
        "  composition_roots: []\n"
        "  allow_concrete_wiring_only_in: []\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "dependency direction violation" in result.stdout


def test_refactoring_guardrail_fails_on_concrete_import_outside_composition_root(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"
    _write(src / "business" / "__init__.py", "")
    _write(src / "business" / "service.py", "from demo_pkg.persistence.http.client import call\n")
    _write(src / "persistence" / "http" / "__init__.py", "")
    _write(src / "persistence" / "http" / "client.py", "def call():\n    return 'ok'\n")

    config = tmp_path / "refactoring.yml"
    config.write_text(
        "version: 1\n"
        "include:\n"
        "  - src\n"
        "ignore: []\n"
        "rules:\n"
        "  ban_wildcard_imports: true\n"
        "  max_relative_import_level: 1\n"
        "  detect_internal_cycles: false\n"
        "  cycle_roots: []\n"
        "  directional_dependencies: []\n"
        "  forbid_concrete_imports:\n"
        "    - scope: demo_pkg.business\n"
        "      forbidden_prefixes:\n"
        "        - demo_pkg.persistence.http\n"
        "  composition_roots:\n"
        "    - demo_pkg.composition_root\n"
        "  allow_concrete_wiring_only_in:\n"
        "    - demo_pkg.composition_root\n",
        encoding="utf-8",
    )

    result = _run_checker(tmp_path, config)

    assert result.returncode == 1
    assert "concrete import violation" in result.stdout
