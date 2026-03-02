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
make package-boundaries-check
make refactoring-guard
make adr-check
make governance-check
```
