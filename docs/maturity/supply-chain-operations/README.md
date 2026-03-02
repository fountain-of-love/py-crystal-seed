# Supply-Chain/Operations Hardening (~80%)

This pillar covers artifact trust and runtime-resilience controls that go beyond the fast local loop.

## Scope

- dependency and vulnerability checks
- SBOM generation and signature verification
- verify-before-publish release trust gates
- runtime-oriented operations hardening gates

## Docs

- [Supply-chain operations](supply-chain-operations.md)
- [Operations hardening gates](operations-hardening-gates.md)
- [Supply-chain/release trust guardrail](supply-chain-release-trust-guardrail.md)
- [Operations hardening guardrail](operations-hardening-guardrail.md)

## Core Commands

```bash
make supplychain-check
make verify-signatures
make ops-gate
make hardening-check
```
