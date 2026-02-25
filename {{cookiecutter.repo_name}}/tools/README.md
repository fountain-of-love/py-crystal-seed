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
