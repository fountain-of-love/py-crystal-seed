# Maturity Status Dashboard

This dashboard tracks current progress toward the Java-style engineering maturity target and highlights the highest-value next improvements.

## Current Snapshot

| Pillar | Score | Status |
| --- | ---: | --- |
| Build/test/type/lint discipline | 95% | Strong |
| Packaging/distribution discipline | 94% | Strong |
| Governance/auditability discipline | 93% | Strong |
| Supply-chain/operations hardening | 80% | Advancing |

Overall maturity estimate: **~92%**

Roadmap reference:
- `docs/maturity/roadmap/guardrail-library-roadmap.md`

## Evidence by Pillar

### 1) Build/Test/Type/Lint (95%)

Signals:
- deterministic local gate via `make check`
- smoke matrix includes lint, typecheck, tests, and version evolution guardrail
- CI coverage for core quality paths

Primary commands:
- `make smoke`
- `make check`

Key docs:
- `docs/maturity/build-quality/README.md`
- `docs/maturity/build-quality/quality-gate-architecture.md`

### 2) Packaging/Distribution (94%)

Signals:
- build/check/install/publish lanes implemented
- release-ready gate validates package quality before release
- GitHub and GitLab release flows include trust gates and manual promotion controls

Primary commands:
- `make package-build`
- `make package-check`
- `make release-ready`

Key docs:
- `docs/maturity/packaging-distribution/README.md`
- `docs/maturity/packaging-distribution/packaging-distribution.md`
- `RELEASING.md`

### 3) Governance/Auditability (93%)

Signals:
- version evolution guardrail enforces facade-only cross-version imports
- compatibility hard rule enforced through protected core contract snapshots
- docs drift, release policy, and waiver governance checks active
- package-boundary import guardrail and ADR quality guardrail active
- externalization strategy defined for migrating guardrail internals into shared libraries

Primary commands:
- `make release-policy`
- `make docs-drift`
- `make waivers-check`

Key docs:
- `docs/maturity/governance-auditability/README.md`
- `docs/maturity/governance-auditability/guardrails-index.md`

### 4) Supply-Chain/Operations Hardening (80%)

Signals:
- dependency scan + SBOM + signature verification lanes are active
- verify-before-publish enforcement in release pipelines
- operations-hardening gates validate perf/leak/recovery/observability behavior

Primary commands:
- `make supplychain-check`
- `make verify-signatures`
- `make ops-gate`
- `make hardening-check`

Key docs:
- `docs/maturity/supply-chain-operations/README.md`
- `docs/maturity/supply-chain-operations/supply-chain-operations.md`

## Highest-Value Next Gaps

1. Supply-chain trust depth
- add external verification consumption/documentation for signed artifacts
- formalize advisory severity policy thresholds + waiver process for vulnerability gates

2. Guardrail library extraction
- in-repo package boundaries completed for governance/release/architecture/ops
- next: publish these boundaries as external shared libraries and switch template dependencies to versioned packages

3. `bubblegum` governance parity
- add refactoring guard
- add coverage governance
- add maturity evidence and guard telemetry/reporting

## Review Cadence

Recommended:
- update this dashboard when major controls are added/removed
- include dashboard delta in release notes for maturity-sensitive changes
