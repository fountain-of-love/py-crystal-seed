# Release Policy Guardrail

## Purpose

Enforce deterministic release governance and reduce accidental unsafe releases.

## Enforcement

Checker:
- `tools/check_release_policy.py`

Command:
- `make release-policy`

## Rules Enforced

1. Semantic version validity
- `pyproject.toml` version must be SemVer-compatible.

2. Tag/version consistency
- release tag must match project version.

3. Changelog coupling
- version bumps in relevant diffs require `CHANGELOG.md` update.

4. Pipeline trust markers
- release pipelines must retain required trust gate markers
  (GitHub and/or GitLab based on available pipeline files).

## CI Integration

GitHub:
- `.github/workflows/release-policy.yml`

GitLab:
- consumed by release jobs before build/sign/publish operations.

## Policy Intent

Release quality is a policy check, not reviewer memory.
