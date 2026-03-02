# Documentation Drift Guardrail

## Purpose

Ensure code/process changes ship with matching documentation updates.

## Enforcement

Checker:
- `tools/check_docs_drift.py`

Command:
- `make docs-drift`

## Rules Enforced

1. Required docs presence
- key project docs must exist.

2. Change-aware update policy
- script/CI/tool/packaging changes require corresponding documentation changes in the same PR.

3. GitHub and GitLab CI awareness
- workflow or pipeline changes must update CI/packaging docs.

## CI Integration

GitHub:
- `.github/workflows/docs-drift.yml`

GitLab:
- intended to run in PR/MR policy lanes where configured.

## Policy Intent

Documentation is treated as an operational dependency, not optional prose.
