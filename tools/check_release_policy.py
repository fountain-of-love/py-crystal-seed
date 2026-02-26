#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def _read_project_version(pyproject: Path) -> str:
    return _read_project_version_from_text(pyproject.read_text(encoding="utf-8"))


def _read_project_version_from_text(text: str) -> str:
    in_project = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            in_project = line == "[project]"
            continue
        if in_project and line.startswith("version"):
            _, value = line.split("=", 1)
            return value.strip().strip('"').strip("'")
    raise RuntimeError("Could not find [project].version in pyproject.toml")


def _version_at_rev(rev: str) -> str | None:
    cmd = ["git", "show", f"{rev}:pyproject.toml"]
    out = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return _read_project_version_from_text(out.stdout)
    except RuntimeError:
        return None


def _git_changed(diff_base: str, diff_head: str) -> set[str]:
    cmd = ["git", "diff", "--name-only", f"{diff_base}...{diff_head}"]
    out = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "git diff failed")
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def _normalized_tag(tag: str) -> str:
    cleaned = tag.replace("refs/tags/", "").strip()
    return cleaned[1:] if cleaned.startswith("v") else cleaned


def main() -> int:
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("[release-policy] pyproject.toml missing")
        return 1

    try:
        version = _read_project_version(pyproject)
    except RuntimeError as exc:
        print(f"[release-policy] {exc}")
        return 1

    if not VERSION_RE.match(version):
        print(f"[release-policy] Invalid SemVer version: {version}")
        return 1

    release_tag = os.environ.get("RELEASE_TAG", "").strip()
    if release_tag:
        tag_version = _normalized_tag(release_tag)
        if tag_version != version:
            print(
                "[release-policy] Tag/version mismatch: "
                f"tag={release_tag!r} -> {tag_version!r}, pyproject={version!r}"
            )
            return 1

    diff_base = os.environ.get("DIFF_BASE", "").strip()
    diff_head = os.environ.get("DIFF_HEAD", "HEAD").strip()
    if diff_base:
        try:
            changed = _git_changed(diff_base=diff_base, diff_head=diff_head)
        except RuntimeError as exc:
            print(f"[release-policy] Unable to evaluate changed files: {exc}")
            return 1

        if "pyproject.toml" in changed:
            previous_version = _version_at_rev(diff_base)
            version_changed = previous_version is not None and previous_version != version
            if version_changed and "CHANGELOG.md" not in changed:
                print(
                    "[release-policy] Version changed in pyproject.toml but "
                    "CHANGELOG.md was not updated."
                )
                return 1

    print(f"[release-policy] OK (version={version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
