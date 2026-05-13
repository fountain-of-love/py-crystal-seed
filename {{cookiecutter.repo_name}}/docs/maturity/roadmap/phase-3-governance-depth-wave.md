# Phase 3 Governance Depth Wave

Purpose:
- define the next implementation wave after guardrail rollout stabilization
- close the remaining maturity gap toward `bubblegum`-level governance rigor
- keep the work aligned with the extracted `guardrails-*` library boundaries

## Why This Wave Is Next

The current rollout established:
- publishable guardrail package boundaries
- stable CLI and wrapper contracts
- GitLab governance/release lanes
- weekly governance reporting baseline
- a deterministic local commit gate

The largest remaining gap is governance depth, not packaging or command shape.

That gap shows up in four areas:
1. coverage governance is still missing
2. maturity evidence is not yet required when production code changes
3. weekly reporting is point-in-time, not trend-oriented
4. the refactoring guard is still a baseline architecture guard, not a full structural policy engine

## Next Wave Scope

### 1) Coverage Governance

Goal:
- treat coverage as governed confidence, not a raw percentage

Deliverables:
- baseline coverage snapshot support
- module/package threshold policy
- parity/non-regression checks
- markdown/json coverage governance output
- CI integration and weekly-report inclusion

Suggested ownership:
- near term: `guardrails-governance`
- later option: split into `guardrails-quality` if the surface grows materially

### 2) Maturity Evidence Guard

Goal:
- require governance evidence when production modules change

Deliverables:
- changed-module detection
- governance evidence contract
- accepted evidence forms:
  - ADR update
  - roadmap update
  - governance log entry
  - explicit governed exception
- additive local extension support

Suggested ownership:
- `guardrails-governance`

### 3) Guard Telemetry and Weekly Trend Reporting

Goal:
- make guardrail health observable over time

Deliverables:
- per-guard runtime and pass/fail summaries
- weekly trend sections
- waiver trend summaries
- docs drift and governance-failure summaries
- markdown/json artifact continuity

Suggested ownership:
- `guardrails-governance` for reporting
- `guardrails-ops` only if runtime/SLI concerns expand substantially

### 4) Refactoring Guard Expansion

Goal:
- strengthen architecture policy enforcement beyond the current baseline

Deliverables:
- directional dependency rules
- ports-over-concretes rules
- composition-root-only concrete wiring rules
- domain/layer purity rules
- manifest-driven cycle scopes and allowlists

Suggested ownership:
- `guardrails-architecture`

## Recommended Order

1. coverage governance
2. maturity evidence guard
3. guard telemetry and weekly trend reporting
4. refactoring guard expansion

Reason:
- coverage governance gives the clearest and most defensible next value signal
- maturity evidence makes governance visible at change time
- telemetry turns the governance system itself into an observable system
- deeper architecture rules should build on the reporting and evidence model

## Acceptance Criteria

This wave is complete when:
- coverage governance is enforceable in CI and visible in weekly reports
- production changes require explicit governance evidence
- weekly governance reporting includes trend, not only snapshot status
- refactoring policy can enforce directional/layered rules declaratively

## Follow-On Wave

After this wave:
- optional domain guard packs
- internal package publication workflow hardening
- downstream upgrade playbooks and compatibility policies
