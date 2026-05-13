# Governance/Auditability Discipline (~93%)

This pillar encodes policy checks that keep architecture evolution explicit and auditable.

## Scope

- version evolution safety rules
- release governance rules
- docs drift governance
- waiver lifecycle governance
- package boundary governance
- refactoring/architecture drift governance
- ADR quality governance
- coverage governance
- maturity evidence enforcement
- weekly governance telemetry and trend reporting
- guardrail library externalization strategy
- guardrail packaging and manifest contracts
- commit lockdown and downstream consumption model
- federated local governance hooks

## Docs

- [Guardrails index](guardrails-index.md)
- [Version evolution guardrail](version-evolution-guardrail.md)
- [Release policy guardrail](release-policy-guardrail.md)
- [Docs drift guardrail](docs-drift-guardrail.md)
- [Waiver governance guardrail](waiver-governance-guardrail.md)
- [Package boundary guardrail](package-boundary-guardrail.md)
- [Refactoring guardrail](refactoring-guardrail.md)
- [ADR quality guardrail](adr-quality-guardrail.md)
- [Coverage governance guardrail](coverage-governance-guardrail.md)
- [Maturity evidence guardrail](maturity-evidence-guardrail.md)
- [Governance log contract](governance-log-contract.md)
- [Weekly governance reporting](weekly-governance-reporting.md)
- [Guard telemetry model](guard-telemetry-model.md)
- [Architecture manifest recipes](architecture-manifest-recipes.md)
- [Guardrail packaging model](guardrail-packaging-model.md)
- [Commit lockdown strategy](commit-lockdown-strategy.md)
- [Guardrail manifest contract](guardrail-manifest-contract.md)
- [Downstream guardrail consumption](downstream-guardrail-consumption.md)
- [Maturity mechanism guardrail](maturity-mechanism-guardrail.md)
- [Guardrail library externalization](guardrail-library-externalization.md)
- [Federated governance hooks](federated-governance-hooks.md)

## Core Commands

```bash
make release-policy
make docs-drift
make waivers-check
make coverage-governance
make maturity-evidence
make package-boundaries-check
make refactoring-guard
make adr-check
make governance-check
```
