# Guardrail Library Roadmap

Purpose:
- define the target state for this template
- define the extraction path from embedded governance to reusable libraries
- define the missing controls required to reach `bubblegum`-level governance rigor

## Target State

The template keeps only:
- stable `make` commands
- stable `tools/check_*.py` adapters
- local configuration files
- project-facing documentation

Shared libraries own the policy engines.

Target public surface:
- Python API
- CLI entrypoints
- packaged resources via `importlib.resources`
- repo-local manifests
- additive local hooks

## Planned Library Split

### 1) `guardrails-architecture`
Owns:
- version evolution import/compatibility checks
- package boundary checks

Status:
- externalized as dependency `guardrails-architecture`
- seed-repo local dev copy: `libs/guardrails-architecture/`
- `tools/check_version_import_boundaries.py`, `tools/check_package_boundaries.py`, and `tools/check_refactoring_guard.py` now target this package boundary

Implemented in Phase 3 wave:
- directional dependency rules
- concrete import restrictions outside composition roots

Planned later:
- composition-only wiring rules
- ports-over-concretes checks

### 2) `guardrails-governance`
Owns:
- docs drift policy
- ADR quality policy
- waiver validation and expiry policy

Status:
- externalized as dependency `guardrails-governance`
- seed-repo local dev copy: `libs/guardrails-governance/`
- `tools/check_docs_drift.py`, `tools/check_adr_quality.py`, and `tools/check_waivers.py` now target this package boundary

Implemented in Phase 3 wave:
- coverage governance
- maturity governance log enforcement
- weekly reporting trend support

Planned later:
- scorecard and roadmap evidence checks
- bypass and exception policy tracking

### 3) `guardrails-release`
Owns:
- SemVer/tag/changelog policy
- CI trust-marker policy for GitHub and GitLab release lanes

Status:
- externalized as dependency `guardrails-release`
- seed-repo local dev copy: `libs/guardrails-release/`
- `tools/check_release_policy.py` now targets this package boundary

Planned later:
- release note enforcement
- release approval evidence
- publish-lane governance bundles

### 4) `guardrails-ops`
Owns:
- perf/leak/recovery/observability gate framework
- reusable gate contracts and result schema

Status:
- externalized as dependency `guardrails-ops`
- seed-repo local dev copy: `libs/guardrails-ops/`
- `tools/run_ops_gates.py` now targets this package boundary

Planned later:
- guard telemetry
- weekly trend export and reporting
- guard pass-rate/runtime SLOs

## Gap To Close Relative To `bubblegum`

Current major gaps:
1. coverage governance (baseline, parity, thresholds)
2. maturity evidence enforcement per changed module
3. guard telemetry and weekly reporting
4. optional domain contract guards (for example OpenAPI)

Packaging and consumption design references:
- `docs/maturity/governance-auditability/guardrail-packaging-model.md`
- `docs/maturity/governance-auditability/guardrail-manifest-contract.md`
- `docs/maturity/governance-auditability/downstream-guardrail-consumption.md`
- `docs/maturity/governance-auditability/commit-lockdown-strategy.md`

## Roadmap Phases

### Phase 1: Finish Internal Separation
Move remaining embedded guard logic into `src/*/guardrails/` modules:
- version evolution
- docs drift
- waiver governance
- release policy
- ops gates

Exit criteria:
- `tools/` scripts are wrappers only
- all guard engines have direct tests

### Phase 2: Extract Shared Libraries
Extract the four guardrail groups into versioned libraries while preserving local command facades.

Progress:
- `guardrails-governance` externalized dependency boundary established
- `guardrails-release` externalized dependency boundary established
- `guardrails-architecture` externalized dependency boundary established
- `guardrails-ops` externalized dependency boundary established

Exit criteria:
- template depends on shared guardrail libraries
- upgrades happen by dependency bumps, not script copy/paste

### Phase 3: Reach `bubblegum` Governance Parity
Add:
- coverage governance
- maturity governance log
- guard telemetry/reporting

Exit criteria:
- architecture drift is blocked structurally
- governance evidence is required for meaningful changes
- guard system is observable and reviewable

Detailed next-wave plan:
- `docs/maturity/roadmap/phase-3-governance-depth-wave.md`

### Phase 4: Add Optional Domain Guard Packs
Examples:
- OpenAPI/documentation contract guards
- migration/database guards
- event/schema guards

These remain opt-in so the template stays lean.

## Priority Order

1. internal separation of current guards
2. extract `guardrails-governance`
3. extract `guardrails-release`
4. extract `guardrails-architecture`
5. extract `guardrails-ops`
6. add coverage governance
7. add maturity evidence guard
8. add guard telemetry and reporting
9. add optional domain guard packs

## Next Recommended Wave

The next implementation wave should focus on governance depth:
1. coverage governance
2. maturity evidence enforcement
3. weekly trend reporting and guard telemetry
4. refactoring guard expansion

Why:
- the packaging and rollout contract is already in place
- the largest remaining maturity gap is governance depth
- these controls most directly close the parity gap with stronger governed reference projects

## Review Rule

When this roadmap changes:
- update this file
- update `docs/maturity/status-dashboard.md` if priorities or maturity expectations changed
- update guardrail docs when ownership moves from template to shared library
