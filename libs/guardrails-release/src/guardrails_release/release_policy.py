from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .result import GuardResult

VERSION_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)

RELEASE_TRUST_RULES: dict[str, tuple[str, ...]] = {
    ".github/workflows/publish-testpypi.yml": (
        "Sign distributions with Sigstore",
        "Enforce signature bundles for all artifacts",
        "Verify signed artifacts in isolated publish job",
    ),
    ".github/workflows/publish-pypi.yml": (
        "Sign distributions with Sigstore",
        "Enforce signature bundles for all artifacts",
        "Verify signed artifacts in isolated publish job",
    ),
    ".gitlab-ci.yml": (
        "gitlab-release-build-sign",
        "gitlab-release-verify-gate",
        "gitlab-release-publish-testpypi",
        "gitlab-release-publish-pypi",
    ),
}


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


def _check_release_trust_workflows(repo_root: Path) -> list[str]:
    violations: list[str] = []
    checked_workflows = 0
    for workflow_path, required_markers in RELEASE_TRUST_RULES.items():
        workflow = repo_root / workflow_path
        if not workflow.exists():
            continue
        checked_workflows += 1
        text = workflow.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                violations.append(
                    f"Workflow {workflow_path} missing required trust step marker: {marker!r}"
                )
    if checked_workflows == 0:
        violations.append(
            "No release pipeline definition found (.github/workflows/* or .gitlab-ci.yml)."
        )
    return violations


def check_release_policy(
    *,
    repo_root: Path,
    release_tag: str,
    diff_base: str,
    diff_head: str,
) -> GuardResult:
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return GuardResult(guard="release_policy", status="fail", violations=[{"message": "pyproject.toml missing"}])

    try:
        version = _read_project_version(pyproject)
    except RuntimeError as exc:
        return GuardResult(guard="release_policy", status="fail", violations=[{"message": str(exc)}])

    violations: list[str] = []
    if not VERSION_RE.match(version):
        violations.append(f"Invalid SemVer version: {version}")

    violations.extend(_check_release_trust_workflows(repo_root))

    if release_tag:
        tag_version = _normalized_tag(release_tag)
        if tag_version != version:
            violations.append(
                "Tag/version mismatch: "
                f"tag={release_tag!r} -> {tag_version!r}, pyproject={version!r}"
            )

    if diff_base:
        try:
            changed = _git_changed(diff_base=diff_base, diff_head=diff_head)
        except RuntimeError as exc:
            violations.append(f"Unable to evaluate changed files: {exc}")
        else:
            if "pyproject.toml" in changed:
                previous_version = _version_at_rev(diff_base)
                version_changed = previous_version is not None and previous_version != version
                if version_changed and "CHANGELOG.md" not in changed:
                    violations.append(
                        "Version changed in pyproject.toml but CHANGELOG.md was not updated."
                    )

    if violations:
        return GuardResult(
            guard="release_policy",
            status="fail",
            violations=[{"message": item} for item in violations],
            metrics={"version": version},
        )

    return GuardResult(guard="release_policy", status="pass", metrics={"version": version})


def format_release_policy_result(result: GuardResult) -> str:
    if result.status == "fail":
        first = result.violations[0]["message"] if result.violations else ""
        if first == "pyproject.toml missing":
            return "[release-policy] pyproject.toml missing"
        if str(first).startswith("Could not find [project].version"):
            return f"[release-policy] {first}"
        lines = ["[release-policy] Release trust workflow policy violations:"]
        if not any("Workflow " in str(item["message"]) or "No release pipeline" in str(item["message"]) for item in result.violations):
            lines = [f"[release-policy] {first}"]
            if len(result.violations) == 1:
                return lines[0]
        lines = ["[release-policy] Release trust workflow policy violations:"] if any("Workflow " in str(item["message"]) or "No release pipeline" in str(item["message"]) for item in result.violations) else [f"[release-policy] {first}"]
        if lines[0].startswith("[release-policy] Release trust"):
            lines.extend(f"  - {item['message']}" for item in result.violations)
            return "\n".join(lines)
        if len(result.violations) > 1:
            lines.extend(f"  - {item['message']}" for item in result.violations[1:])
            return "\n".join(lines)
        return lines[0]
    return f"[release-policy] OK (version={result.metrics.get('version', '')})"


def run_release_policy_check(
    *,
    repo_root: Path,
    release_tag: str,
    diff_base: str,
    diff_head: str,
) -> int:
    result = check_release_policy(
        repo_root=repo_root,
        release_tag=release_tag,
        diff_base=diff_base,
        diff_head=diff_head,
    )
    print(format_release_policy_result(result))
    return result.exit_code()


def main() -> int:
    repo_root_env = os.environ.get("REPO_ROOT", "").strip()
    repo_root = Path(repo_root_env).resolve() if repo_root_env else Path.cwd()
    release_tag = os.environ.get("RELEASE_TAG", "").strip()
    diff_base = os.environ.get("DIFF_BASE", "").strip()
    diff_head = os.environ.get("DIFF_HEAD", "HEAD").strip()
    return run_release_policy_check(
        repo_root=repo_root,
        release_tag=release_tag,
        diff_base=diff_base,
        diff_head=diff_head,
    )
