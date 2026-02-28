# Guardrails Index

This folder is the dedicated home for architecture and governance guardrails.

Purpose:
- make non-negotiable engineering safety rules explicit
- keep agentic coding constraints discoverable
- separate "policy docs" from generic operational docs

## Current Guardrails

1. Version evolution guardrail
   - File: `version-evolution-guardrail.md`
   - Enforces:
     - facade-only cross-version import rule
     - compatibility hard rule for lower-version-used core contracts

2. Operations hardening guardrail
   - Current doc: `../operations-hardening-gates.md`
   - Enforces:
     - performance threshold gate
     - memory growth/leak gate
     - recovery and observability integrity gate

3. Supply-chain and release trust guardrails
   - Current docs:
     - `../supply-chain-operations.md`
     - `../packaging-distribution.md`
     - `../RELEASING.md` (repo root)
   - Enforces:
     - vulnerability scanning and SBOM generation
     - Sigstore signing/verification
     - isolated verify-before-publish gates in CI

4. Release policy guardrail
   - Current doc: `../packaging-distribution.md`
   - Enforces:
     - SemVer/tag/changelog policy
     - release pipeline trust-marker checks

5. Documentation drift guardrail
   - Current doc: `../ci-pipeline.md`
   - Enforces:
     - required-doc presence
     - change-aware docs update policy

6. Waiver governance guardrail
   - Current doc: `../ci-pipeline.md`
   - Enforces:
     - waiver schema validity
     - expiry checks and ownership metadata integrity

## Next Documentation Consolidation

This folder should gain dedicated docs for each guardrail above over time.
The version evolution guardrail is the first one migrated here.
