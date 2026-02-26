from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_guardrail_fails_on_previous_version_internal_import(tmp_path: Path) -> None:
    src = tmp_path / "src" / "demo_pkg"

    _write(src / "__init__.py", "")
    _write(src / "versions" / "__init__.py", "")
    _write(src / "versions" / "v1" / "__init__.py", "")
    _write(src / "versions" / "v1" / "facade.py", "class V1Facade:\n    pass\n")
    _write(src / "versions" / "v1" / "spine.py", "class Spine:\n    pass\n")
    _write(src / "versions" / "v2" / "__init__.py", "")
    _write(
        src / "versions" / "v2" / "module.py",
        "import demo_pkg.versions.v1.spine\n",
    )

    checker = Path(__file__).resolve().parents[1] / "tools" / "check_version_import_boundaries.py"
    env = {
        **os.environ,
        "REPO_ROOT": str(tmp_path),
        "ROOT_PACKAGE": "demo_pkg",
        "VERSION_NAMESPACE": "versions",
    }
    result = subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 1
    assert "forbidden previous-version internal import" in result.stdout
    assert "demo_pkg.versions.v1.spine" in result.stdout
