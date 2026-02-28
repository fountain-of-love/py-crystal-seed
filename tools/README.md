# Tools

This directory contains cross-project guardrails and smoke orchestration helpers.

## `smoke_matrix.sh`

Runs the default smoke matrix:
- Ruff lint/format checks
- Pyright type checks
- pytest suite
- version import-boundary guardrail

Usage:

```bash
./tools/smoke_matrix.sh
```

## `check_version_import_boundaries.py`

Fails when a version module (`vN`) imports internals from `v(N-1)` instead of using the previous facade.

Allowed examples:
- `from pkg.versions.v5 import facade`
- `from pkg.versions.v5 import pkg_v5`

Forbidden examples:
- `from pkg.versions.v5 import spine`
- `import pkg.versions.v5.signals`

## `check_docs_drift.py`

Enforces documentation guardrails:
- required documentation files must exist
- when `DIFF_BASE` is provided, applies change-aware rules (for example, script/CI/tool changes must include doc updates)

Usage:

```bash
./venv/bin/python ./tools/check_docs_drift.py
```

## `check_release_policy.py`

Enforces release policy guardrails:
- `pyproject.toml` version must be SemVer
- on tag builds, tag/version must match
- on PR builds with `DIFF_BASE`, version changes require `CHANGELOG.md` updates
- release pipelines (GitHub and/or GitLab) must retain Sigstore signing, signature-bundle enforcement, and isolated-job verification steps

Usage:

```bash
./venv/bin/python ./tools/check_release_policy.py
```

## `check_waivers.py`

Validates waiver registry policy (`waivers/waivers.yml`):
- required fields present
- `expires` is valid ISO date and not expired
- `approvers` is a non-empty list
- emits CI summary for active/expiring waivers when supported

Usage:

```bash
./venv/bin/python ./tools/check_waivers.py
```
