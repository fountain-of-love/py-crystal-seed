# Guardrails Index

This folder is the dedicated home for architecture and governance guardrails.

Purpose:
- make non-negotiable engineering safety rules explicit
- keep agentic coding constraints discoverable
- separate "policy docs" from generic operational docs

## Current Guardrails

1. Version evolution guardrail
   - File: [version-evolution-guardrail.md](version-evolution-guardrail.md)
   - Enforces:
     - facade-only cross-version import rule
     - compatibility hard rule for lower-version-used core contracts

2. Operations hardening guardrail
   - File: [../supply-chain-operations/operations-hardening-guardrail.md](../supply-chain-operations/operations-hardening-guardrail.md)
   - Enforces:
     - performance threshold gate
     - memory growth/leak gate
     - recovery and observability integrity gate

3. Supply-chain and release trust guardrails
   - File: [../supply-chain-operations/supply-chain-release-trust-guardrail.md](../supply-chain-operations/supply-chain-release-trust-guardrail.md)
   - Enforces:
     - vulnerability scanning and SBOM generation
     - Sigstore signing/verification
     - isolated verify-before-publish gates in CI

4. Release policy guardrail
   - File: [release-policy-guardrail.md](release-policy-guardrail.md)
   - Enforces:
     - SemVer/tag/changelog policy
     - release pipeline trust-marker checks

5. Documentation drift guardrail
   - File: [docs-drift-guardrail.md](docs-drift-guardrail.md)
   - Enforces:
     - required-doc presence
     - change-aware docs update policy

6. Waiver governance guardrail
   - File: [waiver-governance-guardrail.md](waiver-governance-guardrail.md)
   - Enforces:
     - waiver schema validity
     - expiry checks and ownership metadata integrity

7. Package boundary guardrail
   - File: [package-boundary-guardrail.md](package-boundary-guardrail.md)
   - Enforces:
     - explicit cross-package import boundaries
     - configuration-driven architecture isolation policy

8. Refactoring guardrail
   - File: [refactoring-guardrail.md](refactoring-guardrail.md)
   - Enforces:
     - wildcard import bans
     - relative import depth discipline
     - internal dependency cycle prevention

9. ADR quality guardrail
   - File: [adr-quality-guardrail.md](adr-quality-guardrail.md)
   - Enforces:
     - decision-record template and metadata quality
     - minimum alternatives and explicit tradeoff capture

10. Maturity mechanism guardrail
   - File: [maturity-mechanism-guardrail.md](maturity-mechanism-guardrail.md)
   - Enforces:
     - single maturity-based docs structure
     - status dashboard + adoption mechanism continuity

11. Guardrail library externalization guardrail
   - File: [guardrail-library-externalization.md](guardrail-library-externalization.md)
   - Enforces:
     - stable local command facade for guardrails
     - planned migration path from in-repo policy logic to shared versioned libraries

12. Federated governance hook guardrail
   - File: [federated-governance-hooks.md](federated-governance-hooks.md)
   - Enforces:
     - central shared guardrails remain mandatory
     - project-specific local governance can be added without forking central policy

## Rollout Architecture Docs

These documents define the rollout target for making guardrails publishable, declarative, and consumption-ready across projects.

13. Guardrail packaging model
   - File: [guardrail-packaging-model.md](guardrail-packaging-model.md)
   - Defines:
     - canonical package structure
     - stable Python API and CLI surface
     - package-data and SemVer rules

14. Commit lockdown strategy
   - File: [commit-lockdown-strategy.md](commit-lockdown-strategy.md)
   - Defines:
     - commit, CI, release, and weekly enforcement tiers
     - full-governance target for agentic development

15. Guardrail manifest contract
   - File: [guardrail-manifest-contract.md](guardrail-manifest-contract.md)
   - Defines:
     - repo-local manifest ownership
     - package-owned schemas/defaults
     - result envelope and config resolution rules

16. Downstream guardrail consumption
   - File: [downstream-guardrail-consumption.md](downstream-guardrail-consumption.md)
   - Defines:
     - internal-package consumption model
     - pre-commit and GitLab CI integration
     - additive local hook extension model

## Related Operational Docs

- [operations-hardening-gates.md](../supply-chain-operations/operations-hardening-gates.md)
- [supply-chain-operations.md](../supply-chain-operations/supply-chain-operations.md)
- [packaging-distribution.md](../packaging-distribution/packaging-distribution.md)
- [ci-pipeline.md](../build-quality/ci-pipeline.md)
- [RELEASING.md](../../RELEASING.md)
