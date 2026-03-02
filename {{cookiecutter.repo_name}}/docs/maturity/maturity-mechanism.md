# Maturity Mechanism (Adoption Guide)

This is the reusable mechanism projects should adopt when leveraging this template.

## Why Use It

It turns abstract quality ambitions into a concrete operating model:
- clear maturity targets
- explicit guardrails
- deterministic validation commands
- traceable progress over time

This is especially useful for agentic coding contexts where implicit architecture rules are easy to violate.

## The Mechanism

Use one unified documentation and governance structure mapped to four pillars:

1. Build/test/type/lint discipline
2. Packaging/distribution discipline
3. Governance/auditability discipline
4. Supply-chain/operations hardening

For each pillar:
- define current target score (or range)
- define controls and commands
- define enforcement points (local + CI)
- define next highest-value gaps

## Minimum Adoption Checklist

1. Create a maturity docs root:
- `docs/maturity/`

2. Create pillar folders:
- `docs/maturity/build-quality/`
- `docs/maturity/packaging-distribution/`
- `docs/maturity/governance-auditability/`
- `docs/maturity/supply-chain-operations/`

3. Create two anchor docs:
- `docs/README.md` (single index/entrypoint)
- `docs/maturity/status-dashboard.md` (live maturity snapshot + next gaps)

4. Ensure command-level enforceability:
- fast quality lane (`make check`)
- release trust lane (`make supplychain-check`, signing/verify gates)
- operations lane (`make ops-gate`)
- governance lane (`make release-policy`, `make docs-drift`, `make waivers-check`)

5. Add guardrail docs under maturity governance:
- version evolution guardrail
- release policy guardrail
- docs drift guardrail
- waiver governance guardrail
- package boundary guardrail
- ADR quality guardrail
- guardrail library externalization strategy

6. Keep docs and enforcement coupled:
- changes in tooling/workflows should require docs updates in the same PR.

## Review Rhythm

Recommended:
- update `status-dashboard.md` when adding/removing controls
- include maturity deltas in release notes for major process changes

## Expected Outcome

Teams get:
- less ambiguity in engineering standards
- safer autonomous contribution paths
- clearer justification for “overhead” via visible risk reduction and release confidence

Related governance guardrail:
- `docs/maturity/governance-auditability/maturity-mechanism-guardrail.md`
