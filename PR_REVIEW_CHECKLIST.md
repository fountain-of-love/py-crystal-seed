# PR Review Checklist (Cross-Project)

Use this checklist during PR review. It maps directly to buckets `A` through `G` in the developer guide.

## A) Verification & Test Confidence
- [ ] Acceptance criteria are captured as executable behavior scenarios.
- [ ] Tests are layered appropriately (`smoke`, `core behavior`, `resilience/edge`).
- [ ] New defects include focused non-regression coverage.
- [ ] Scenario tags enable targeted execution.
- [ ] Fixtures/helpers are deterministic and minimal.
- [ ] Assertions focus on behavior, not internals.

## B) Architecture Integrity
- [ ] Boundary contracts (capabilities, payloads, errors) are explicit.
- [ ] Critical invariants are enforced at entry/persistence/state-transition points.
- [ ] Contract/invariant checks are centralized and reusable.
- [ ] Policy logic is separated from mechanism.
- [ ] Dependency direction remains explicit and clean.
- [ ] Failure paths use predictable, typed domain errors (or equivalent).

## C) Evolution & Compatibility Safety
- [ ] Existing public behavior is preserved unless change is explicit.
- [ ] Parity/non-regression checks cover adjacent versions/implementations.
- [ ] Changes are additive or extension-based where possible.
- [ ] Deprecation path is defined before removal.
- [ ] Data/protocol compatibility across transitions is validated.
- [ ] Breaking changes include migration notes and test evidence.

## D) Operational Governance & Continuity
- [ ] Docs/runbooks/migration notes are updated in the same PR when needed.
- [ ] Significant architecture decisions are recorded (ADR or equivalent).
- [ ] Validation commands are deterministic and runnable locally.
- [ ] Default contributor command set remains accurate.
- [ ] Drift checks protect required docs/scripts/critical paths.
- [ ] Ownership/escalation guidance is clear for affected areas.

## E) Human Governance & Policy Enforcement
- [ ] High-impact actions have explicit human approval controls.
- [ ] Authorization is enforced for execute/approve/publish boundaries.
- [ ] Both approvals and denials are auditable with actor/context metadata.
- [ ] Least-privilege defaults are maintained.
- [ ] Resume/retry/replay flows re-check permissions.
- [ ] Policy inputs are validated to prevent bypass paths.

## F) Data Continuity, Replay & Lineage
- [ ] Persisted history supports replay/recovery.
- [ ] Run/version/source identity remains intact across lifecycle flows.
- [ ] Lineage/provenance links are persisted for derived artifacts.
- [ ] Event/schema envelopes are explicit and versioned.
- [ ] Replay integrity is validated before applying state mutations.
- [ ] Deterministic reconstruction from persisted records is possible.

## G) Observability & Resilience by Design
- [ ] Telemetry channels are separated by concern (state/audit/ops).
- [ ] Anomalies are recorded as structured events/metrics/summaries.
- [ ] Fault-handling modes (skip/degrade/raise) are explicit and tested.
- [ ] Correlation IDs connect runtime, audit, and incident signals.
- [ ] Retention/rotation policy exists for operational data.
- [ ] Recovery outcomes are measured, not only failures.

## PR Decision
- [ ] Approve: all relevant checks pass.
- [ ] Request changes: failed checks are listed with concrete remediation.
