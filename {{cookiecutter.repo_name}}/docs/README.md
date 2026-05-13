# Documentation Index

This documentation is organized around the project maturity model aligned to a Java-style engineering target.

Design objective:
- every commit should preserve high code quality and architectural integrity
- autonomous/agentic changes must remain safe, auditable, and reversible

## Maturity Targets

1. Build/test/type/lint discipline: ~95%
2. Packaging/distribution discipline: ~94%
3. Governance/auditability discipline: ~93%
4. Supply-chain/operations hardening: ~80%

Live status and next-gap view:
- [Maturity status dashboard](maturity/status-dashboard.md)
Adoption mechanism for downstream projects:
- [Maturity mechanism](maturity/maturity-mechanism.md)
Roadmap for extracting guardrails into shared libraries:
- [Guardrail library roadmap](maturity/roadmap/guardrail-library-roadmap.md)
Next implementation wave:
- [Phase 3 governance depth wave](maturity/roadmap/phase-3-governance-depth-wave.md)

## Unified Structure

### 1) Build/Test/Type/Lint (~95%)
- [Pillar index](maturity/build-quality/README.md)
- [Quality gate architecture](maturity/build-quality/quality-gate-architecture.md)
- [CI pipeline](maturity/build-quality/ci-pipeline.md)
- [Make command frontdoor](maturity/build-quality/make.md)

### 2) Packaging/Distribution (~94%)
- [Pillar index](maturity/packaging-distribution/README.md)
- [Packaging and distribution](maturity/packaging-distribution/packaging-distribution.md)
- [Releasing playbook](../RELEASING.md)

### 3) Governance/Auditability (~93%)
- [Pillar index](maturity/governance-auditability/README.md)
- [Guardrails index](maturity/governance-auditability/guardrails-index.md)
- [Version evolution guardrail](maturity/governance-auditability/version-evolution-guardrail.md)
- [Release policy guardrail](maturity/governance-auditability/release-policy-guardrail.md)
- [Docs drift guardrail](maturity/governance-auditability/docs-drift-guardrail.md)
- [Waiver governance guardrail](maturity/governance-auditability/waiver-governance-guardrail.md)
- [Package boundary guardrail](maturity/governance-auditability/package-boundary-guardrail.md)
- [Refactoring guardrail](maturity/governance-auditability/refactoring-guardrail.md)
- [ADR quality guardrail](maturity/governance-auditability/adr-quality-guardrail.md)
- [Guardrail library externalization](maturity/governance-auditability/guardrail-library-externalization.md)
- [Guardrail packaging model](maturity/governance-auditability/guardrail-packaging-model.md)
- [Commit lockdown strategy](maturity/governance-auditability/commit-lockdown-strategy.md)
- [Guardrail manifest contract](maturity/governance-auditability/guardrail-manifest-contract.md)
- [Downstream guardrail consumption](maturity/governance-auditability/downstream-guardrail-consumption.md)
- [Federated governance hooks](maturity/governance-auditability/federated-governance-hooks.md)
- [Maturity mechanism guardrail](maturity/governance-auditability/maturity-mechanism-guardrail.md)
- [ADR templates](adr/README.md)

### 4) Supply-Chain/Operations Hardening (~80%)
- [Pillar index](maturity/supply-chain-operations/README.md)
- [Supply-chain operations](maturity/supply-chain-operations/supply-chain-operations.md)
- [Operations hardening gates](maturity/supply-chain-operations/operations-hardening-gates.md)
- [Supply-chain/release trust guardrail](maturity/supply-chain-operations/supply-chain-release-trust-guardrail.md)
- [Operations hardening guardrail](maturity/supply-chain-operations/operations-hardening-guardrail.md)

## Background/Reference

- [Reference docs](reference/)
