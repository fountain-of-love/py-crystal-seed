# Maturity Mechanism Guardrail

## Purpose

Keep maturity progress explicit, reviewable, and operationally useful across projects generated from this template.

This guardrail prevents maturity intent from drifting into ad-hoc process.

## Policy

Projects using this template should maintain:
1. a unified maturity structure in `docs/maturity/` aligned to the four pillars
2. a live maturity snapshot in `docs/maturity/status-dashboard.md`
3. an adoption mechanism doc in `docs/maturity/maturity-mechanism.md`

## Enforcement

Primary guard:
- `tools/check_docs_drift.py` requires `docs/maturity/maturity-mechanism.md` presence.

Related governance checks:
- `make docs-drift`
- `make release-policy`
- `make waivers-check`

## Review Expectations

When controls are added/changed:
1. update the relevant pillar docs
2. update `status-dashboard.md` if maturity score/gaps changed
3. include rationale in PR notes for governance visibility

## Why This Is a Guardrail

Without this, teams can keep tooling while losing architectural intent and maturity accountability.

This guardrail ensures:
- maturity targets stay visible
- contributors share one structure
- process overhead has explicit risk-reduction context
