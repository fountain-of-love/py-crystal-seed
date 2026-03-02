# Tools

This directory contains cross-project guardrails and smoke orchestration helpers.

## `smoke_matrix.sh`

Runs the default smoke matrix:
- Ruff lint/format checks
- Pyright type checks
- pytest suite
- version evolution guardrail (import boundaries + compatibility contracts)
- package boundary guardrail (config-driven cross-package import rules)
- refactoring guardrail (wildcard import, relative import depth, internal cycle checks)
- ADR quality guardrail (naming/template consistency)

Usage:

```bash
./tools/smoke_matrix.sh
```

## `../scripts/run_commit_gate.sh`

Runs the local commit gate:
- delegates to `pre-commit` when the dev toolchain is installed in `venv`
- fails clearly when required commit-time modules are missing
- is the canonical local commit entrypoint used by the repo-owned git hook

## `check_version_import_boundaries.py`

Runs the version evolution guardrail:
- Cross-version import rule: `vN` cannot import internals from `v(N-1)`; facade-only is allowed.
- Compatibility hard rule: core contracts used by lower versions must remain stable.

Allowed examples:
- `from pkg.versions.v5 import facade`
- `from pkg.versions.v5 import pkg_v5`

Forbidden examples:
- `from pkg.versions.v5 import spine`
- `import pkg.versions.v5.signals`

Compatibility contract file:
- `tools/version_evolution_contracts.json`
- implemented as a thin CLI wrapper over `guardrails-architecture` (`guardrails_architecture.version_evolution`)

Refresh contract intentionally:

```bash
./venv/bin/python ./tools/check_version_import_boundaries.py --write-contract
```

## `check_docs_drift.py`

Enforces documentation guardrails:
- required documentation files must exist
- when `DIFF_BASE` is provided, applies change-aware rules (for example, script/CI/tool changes must include doc updates)
- implemented as a thin CLI wrapper over `guardrails-governance` (`guardrails_governance.docs_drift`)

Usage:

```bash
./venv/bin/python ./tools/check_docs_drift.py
```

## `check_package_boundaries.py`

Enforces package boundary policy from `tools/package_boundaries.yml`:
- prevents forbidden imports between sibling packages/subsystems
- supports strict architecture isolation across domains
- implemented as a thin CLI wrapper over `guardrails-architecture` (`guardrails_architecture.package_boundaries`)

Usage:

```bash
./venv/bin/python ./tools/check_package_boundaries.py
```

## `check_refactoring_guard.py`

Runs the generic structural refactoring guard:
- forbids wildcard imports
- limits relative import depth
- detects internal dependency cycles in the root package
- implemented as a thin CLI wrapper over `guardrails-architecture` (`guardrails_architecture.refactoring_guard`)

Config file:
- `tools/refactoring_guardrails.yml`

Usage:

```bash
./venv/bin/python ./tools/check_refactoring_guard.py
```

## `check_adr_quality.py`

Validates ADR quality and structure:
- canonical file naming
- required front-matter metadata
- required decision sections + alternatives + tradeoff markers
- implemented as a thin CLI wrapper over `guardrails-governance` (`guardrails_governance.adr_quality`)

Usage:

```bash
./venv/bin/python ./tools/check_adr_quality.py
```

## `check_release_policy.py`

Enforces release policy guardrails:
- `pyproject.toml` version must be SemVer
- on tag builds, tag/version must match
- on PR builds with `DIFF_BASE`, version changes require `CHANGELOG.md` updates
- release pipelines (GitHub and/or GitLab) must retain Sigstore signing, signature-bundle enforcement, and isolated-job verification steps
- implemented as a thin CLI wrapper over `guardrails-release` (`guardrails_release.release_policy`)

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
- implemented as a thin CLI wrapper over `guardrails-governance` (`guardrails_governance.waivers`)

Usage:

```bash
./venv/bin/python ./tools/check_waivers.py
```

## `run_ops_gates.py`

Runs operational hardening checks:
- performance threshold check
- memory growth/leak check
- recovery/retry behavior check
- observability event integrity check (structured events + correlation IDs)
- implemented as a thin CLI wrapper over `guardrails-ops` (`guardrails_ops.ops`)

Usage:

```bash
./venv/bin/python ./tools/run_ops_gates.py
```

## Guardrail Externalization Strategy

These scripts are intentionally stable command-level facades (`tools/*.py`).
As governance logic matures, move heavy policy internals into versioned shared libraries while keeping these entrypoints stable.

Benefits:
- template stays lean
- downstream projects adopt improvements by bumping library versions
- local command UX and CI integration remain unchanged

Current state:
- guardrail engines are treated as external library dependencies
- in this template repo, local development copies live under `libs/*` and are installed/editable in bootstrap
- generated projects should consume published versions and upgrade guard behavior by dependency bump
- generated projects may add local policy through `project_governance/hooks.py`
- wrappers always run central guardrails first; local hooks run only after central pass

Target reusable contract:
- Python package dependency
- CLI entrypoint
- repo-local manifest/config
- additive local hook

Decluttering rule:
- do not grow `tools/` with more policy logic
- keep new guard behavior in shared `guardrails-*` libraries
- treat the cookiecutter copy as adapter/config/docs surface, not as the long-term home of governance internals

## Federated Governance Hook

Derived projects can add local governance extensions in `project_governance/hooks.py`.

Contract:
- central `guardrails-*` library check runs first
- local hook runs second only if the central check passes
- local hook may tighten policy and fail the command
- local hook must not bypass or replace the central baseline

See:
- `docs/maturity/governance-auditability/federated-governance-hooks.md`
- `docs/maturity/governance-auditability/guardrail-packaging-model.md`
- `docs/maturity/governance-auditability/commit-lockdown-strategy.md`
- `docs/maturity/governance-auditability/guardrail-manifest-contract.md`
- `docs/maturity/governance-auditability/downstream-guardrail-consumption.md`
