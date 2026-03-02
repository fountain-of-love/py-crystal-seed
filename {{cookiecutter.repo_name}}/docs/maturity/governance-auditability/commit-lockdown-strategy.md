# Commit Lockdown Strategy

Purpose:
- define how commits, merge requests, releases, and weekly runs enforce governance
- make agentic development comply with the same guardrails as human development
- ensure every relevant guard runs automatically on the right enforcement surface

## Goal

Target state:
- commits are blocked when central governance fails
- local hooks may tighten policy, never weaken it
- CI and scheduled lanes enforce the same maturity model with appropriate depth
- no direct bypass path exists for agent-generated changes

## Enforcement Tiers

### Tier A: Commit-Time

Target state: full governance.

`pre-commit` must run:
- Ruff lint/format check
- Pyright
- tests
- version evolution
- package boundaries
- refactoring guard
- docs drift
- ADR quality
- waivers
- release policy

Rules:
- commit-time performance should improve through diff-aware execution where supported
- if a guard is not yet diff-aware, it still runs globally until optimized
- `pre-commit` is a governance gate, not just a style gate

## Tier B: Merge Request / Branch CI

GitLab CI must run:
- `make smoke`
- `make governance-check`
- `make ops-gate` on merge requests and branches
- package/release verification on tags

Required GitLab job additions:
- `quality_governance`
- keep `ops_gates`

## Tier C: Release

Tag/release lane must run:
- release policy
- build
- twine check
- signing
- signature verification
- SBOM
- dependency scan
- publish approvals

Release policy remains blocking.
Publish remains approval-gated.

## Tier D: Weekly Scheduled Governance

Chosen default: always report.

Scheduled GitLab pipeline must:
- run governance summary checks
- emit a weekly report even when there are no findings
- explicitly include `no action required` when clean
- store the report as a CI artifact and summarize it in logs

Initial weekly report should include:
- current package versions for all `guardrails-*`
- summary of guard status by package
- active waivers count
- expiring waivers count
- docs drift findings
- recent guard failures if available
- clean/noisy status summary

Later additions:
- guard runtime trends
- failure-rate trends
- bypass and waiver trend dashboard
- false-positive tracking

## Commit Lockdown Matrix

| Surface | Enforcement | Required guards |
| --- | --- | --- |
| `pre-commit` | blocking | lint, typecheck, tests, version evolution, package boundaries, refactoring, docs drift, ADR, waivers, release policy |
| `make smoke` | blocking | lint, typecheck, tests, version evolution, package boundaries, refactoring, ADR |
| `make governance-check` | blocking | docs drift, waivers, release policy, package boundaries, refactoring, ADR |
| GitLab MR/branch CI | blocking | `make smoke`, `make governance-check`, `make ops-gate` |
| GitLab tag/release CI | blocking | release policy, build, twine check, signing, verification, SBOM, vulnerability scan, manual publish approvals |
| Weekly schedule | reporting | always emit governance report with clean/noisy status, expiring waivers, drift findings, failures, trend metrics |

## Optimization Policy

Full governance remains mandatory.
Speed comes from:
- diff-aware execution
- caching
- shared result schema
- consistent config loading

Speed does not come from silently dropping checks from the commit gate.

## Agentic Development Policy

Agent-generated commits are subject to the same lanes as human commits.
Rules:
- no direct bypass path
- failures must be actionable and typed
- central guardrails run before local hooks
- local hooks may add failures, never suppress central ones

## Required Implementation Targets

The rollout target requires:
- `.pre-commit-config.yaml` expanded to the full governance set
- `.gitlab-ci.yml` gains at least:
  - `quality_governance`
  - `weekly_governance_report`
- weekly report output stored as CI artifacts and summarized in logs

## Acceptance Criteria

- there is one canonical enforcement matrix in project docs
- README and developer docs point to it
- no ambiguity remains about which guard runs where
- weekly reporting expectations are explicit and testable

## Related Docs

- `guardrail-packaging-model.md`
- `guardrail-manifest-contract.md`
- `downstream-guardrail-consumption.md`
