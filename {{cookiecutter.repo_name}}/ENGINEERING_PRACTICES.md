# Cross-Project Engineering Practices (Reusable)

These practices are intentionally tool-agnostic and can be reused across repositories.

## Quick Start (Apply A-G in This Repo)

Use this sequence for day-to-day implementation and review:

1. Define behavior first (`A`): write/adjust acceptance scenarios and targeted non-regression tests.
2. Keep boundaries explicit (`B`): preserve contracts, invariants, and typed failure paths.
3. Change safely (`C`): prefer additive extension, keep compatibility stable unless explicitly broken.
4. Keep ops docs current (`D`): update runbooks/docs/notes in the same PR as code changes.
5. Enforce human/policy controls (`E`) for high-impact actions and auditable decisions.
6. Preserve continuity (`F`): keep lineage, replayability, and deterministic reconstruction intact.
7. Validate resilience signals (`G`): ensure telemetry, fault modes, and recovery outcomes are observable.

For this template specifically: run `make check` before finalizing, and if you change defaults, update both root files and `{{cookiecutter.repo_name}}/` equivalents.

## A) Verification & Test Confidence

### Practices

- **Define acceptance criteria as executable behavior scenarios.**  
  Why: This aligns implementation with user-visible outcomes and prevents scope drift.  
  How: Write scenarios in plain, domain language. Keep each scenario focused on one behavior. Run them in CI as release gates.
- **Organize test suites by risk and runtime cost (`smoke`, `core behavior`, `resilience/edge`).**  
  Why: Teams need both fast confidence and deep confidence without slowing every change.  
  How: Classify tests by intent and expected duration. Run smoke tests on every change. Run broader suites at merge and release stages.
- **Add focused non-regression tests whenever a defect is fixed.**  
  Why: This prevents repeat incidents and makes defect learning permanent.  
  How: Reproduce the bug with a minimal failing scenario. Add the scenario before or with the fix. Keep assertions limited to the observed failure mode.
- **Tag and segment scenarios so teams can run targeted subsets quickly.**  
  Why: Selective execution speeds feedback during development and triage.  
  How: Use stable tags for risk, feature area, and execution profile. Document standard filtered commands. Keep tag semantics consistent across test files.
- **Keep fixture/setup helpers shared, small, and deterministic.**  
  Why: Large ad-hoc setup creates flaky tests and high maintenance cost.  
  How: Centralize setup logic in thin helpers. Remove randomness and non-deterministic defaults. Include only data required by the scenario.
- **Prefer behavior assertions over implementation-detail assertions.**  
  Why: Behavior-level tests survive refactors and reflect real system value.  
  How: Assert outputs, state transitions, and boundary contracts. Avoid assertions on private call order unless absolutely required. Refactor tests when internal coupling appears.

### Shared Principles

- **Behavioral correctness is the primary quality signal.**  
  Why: Shipping correct behavior matters more than local implementation elegance.  
  How: Prioritize acceptance outcomes in review. Block release on unmet behavior criteria. Use implementation metrics as support, not as the final gate.
- **Fast feedback and deep validation must coexist.**  
  Why: Speed without depth misses risk, and depth without speed kills delivery flow.  
  How: Design a layered pipeline with clear stages. Keep fast suites mandatory and cheap. Schedule deep suites predictably so teams trust them.
- **Test assets should be readable by both technical and non-technical contributors.**  
  Why: Shared understanding reduces requirement ambiguity and review friction.  
  How: Use business language in scenario text. Keep step names explicit and concise. Avoid framework-specific jargon in acceptance artifacts.
- **Test intent must remain stable even when internals are refactored.**  
  Why: Brittle tests block healthy design evolution.  
  How: Anchor tests to public behavior and contracts. Isolate implementation-sensitive checks into narrow unit tests. Update tests only when behavior intent changes.
- **Reliability of tests is part of product reliability.**  
  Why: Flaky or inconsistent tests undermine trust in every release decision.  
  How: Track flake rate as a quality metric. Quarantine and fix flaky tests quickly. Treat persistent flakiness as production risk.

## B) Architecture Integrity

### Practices

- **Define explicit contracts at module/service boundaries (capabilities, payload shape, error shape).**  
  Why: Implicit boundaries cause hidden coupling and surprise breakages.  
  How: Publish interface definitions in code. Validate these contracts in tests and runtime guards. Treat contract changes as explicit change events.
- **Enforce critical invariants at entry points, persistence boundaries, and state transitions.**  
  Why: Invalid data is cheapest to stop at boundaries before it spreads.  
  How: Add assertive checks where data enters. Re-validate persisted data on load. Guard every state mutation path with invariant checks.
- **Keep contract checks centralized and reusable to avoid drift.**  
  Why: Duplicated validation logic diverges over time and weakens guarantees.  
  How: Create shared validators and assertion helpers. Call them from all boundary layers. Version them carefully as contracts evolve.
- **Separate policy decisions from mechanism so each can evolve safely.**  
  Why: Mixing policy with execution logic increases blast radius for simple rule changes.  
  How: Isolate policy logic in dedicated modules. Inject policy into orchestration rather than hard-coding it. Test policy behavior independently of transport and storage.
- **Prefer narrow interfaces and explicit dependency direction.**  
  Why: Broad interfaces hide accidental dependencies and complicate replacement.  
  How: Expose only the methods a consumer needs. Enforce dependency direction with import rules and review checks. Refactor broad interfaces when unrelated methods accumulate.
- **Use typed domain errors (or equivalent) for predictable failure handling.**  
  Why: Generic errors force brittle string matching and ambiguous recovery behavior.  
  How: Define explicit error categories. Map each category to a standard handling path. Keep user-facing and operational messaging consistent per error type.

### Shared Principles

- **Boundaries must be explicit, testable, and stable.**  
  Why: Stable boundaries let teams change internals independently without regressions.  
  How: Formalize interfaces and expected behaviors. Write boundary-focused tests for normal and failure paths. Keep compatibility promises visible in docs and review checklists.
- **Invalid state should fail early with precise diagnostics.**  
  Why: Late failures are harder to debug and recover from.  
  How: Validate assumptions at the first trustworthy boundary. Emit actionable messages with context and expected shape. Avoid silent correction of corrupted inputs.
- **Architectural safety should be encoded in code, not only in convention.**  
  Why: Conventions alone degrade under delivery pressure.  
  How: Add runtime guards for critical invariants. Use static checks for dependency and import rules. Enforce with CI so rules are consistently applied.
- **Cohesion and separation of concerns reduce change blast radius.**  
  Why: Tightly focused modules are easier to reason about and safer to modify.  
  How: Group code by change reason, not by convenience. Split modules that mix policy, orchestration, and storage concerns. Keep cross-cutting behavior behind explicit adapters.
- **Clarity at interfaces is more valuable than clever internals.**  
  Why: Most defects occur at integration edges, not inside isolated algorithms.  
  How: Prefer explicit names and predictable payloads. Keep interface behavior unsurprising and documented. Optimize internals only after interface clarity is solid.

## C) Evolution & Compatibility Safety

### Practices

- **Treat existing public behavior as stable by default.**  
  Why: Stability protects downstream users and reduces upgrade risk.  
  How: Require explicit approval for any intentional behavior break. Document rationale and expected impact. Add tests that prove old behavior is preserved where promised.
- **Use parity/non-regression checks between adjacent versions or implementations.**  
  Why: Parity tests catch subtle drift that unit tests often miss.  
  How: Compare equivalent flows, outputs, and event sequences. Keep comparison fixtures stable and representative. Run parity checks in the default release pipeline.
- **Evolve via extension/composition and additive APIs rather than in-place semantic rewrites.**  
  Why: Additive change preserves history and lowers migration cost.  
  How: Introduce new behavior behind extension seams. Keep prior contracts intact for existing consumers. Prefer wrappers/adapters over changing old semantics directly.
- **Deprecate before removing and provide explicit migration windows.**  
  Why: Abrupt removal creates operational disruption and trust loss.  
  How: Mark deprecated paths in code and docs. Publish timelines and replacement options. Enforce removal only after the window closes.
- **Preserve data and protocol compatibility across version transitions.**  
  Why: Incompatible state formats can break replay, resume, and interoperability.  
  How: Version data envelopes explicitly. Validate transition rules with migration tests. Keep compatibility shims where short-term bridging is needed.
- **Make breaking changes explicit with migration notes and test evidence.**  
  Why: Invisible breaks cause hidden outages during adoption.  
  How: Document the break, who is affected, and required actions. Include before/after examples. Link tests that demonstrate intended new behavior.

### Shared Principles

- **Compatibility is a product requirement, not an afterthought.**  
  Why: Reliable upgrades are part of user value and adoption.  
  How: Evaluate compatibility in design review and PR gates. Assign explicit owners for compatibility risk. Treat regressions as product defects, not maintenance noise.
- **Change intent must be explicit and observable in tests.**  
  Why: Unclear intent leads to accidental drift and hard-to-review changes.  
  How: Link each change to a specific expected behavior. Add tests that show before/after outcomes. Keep intent statements in PR descriptions and docs.
- **Reuse should reduce accidental complexity without hiding behavioral evolution.**  
  Why: Over-abstraction can erase important semantics and learning context.  
  How: Extract shared mechanics only when differences stay visible. Keep version-specific behavior explicit at boundaries. Revert abstractions that obscure intent.
- **Evolution should be narratable and reversible where feasible.**  
  Why: Teams need clear reasoning to debug, audit, and roll back safely.  
  How: Maintain migration narratives and ADR links. Prefer reversible rollouts for risky changes. Keep rollback procedures tested and documented.
- **Historical behavior is part of system trust.**  
  Why: Users rely on prior guarantees when adopting new versions.  
  How: Preserve old semantics where promised. Provide explicit alternatives when behavior must change. Validate historical flows with dedicated scenarios.

## D) Operational Governance & Continuity

### Practices

- **Keep architecture docs, migration notes, and runbooks updated in the same change as code.**  
  Why: Stale operational knowledge creates incident risk and onboarding friction.  
  How: Require doc updates whenever behavior or structure changes. Review docs in the same PR as implementation. Fail doc-drift checks when required updates are missing.
- **Capture significant technical decisions in lightweight ADRs with tradeoffs and validation links.**  
  Why: Undocumented decisions get relitigated and context is lost.  
  How: Record context, decision, alternatives, and consequences in a small template. Link validation evidence and affected docs. Keep ADRs indexed by chronology.
- **Maintain one predictable local validation flow with environment overrides for portability.**  
  Why: Inconsistent local setup slows development and hides issues until CI.  
  How: Publish one default command path for local validation. Support controlled overrides for filesystem and environment constraints. Keep commands platform-neutral where possible.
- **Define a default contributor command set for setup, test, and smoke validation.**  
  Why: Clear defaults reduce cognitive load and onboarding time.  
  How: Document canonical commands in one location. Keep examples copy-pastable and current. Verify command health in CI to prevent drift.
- **Add lightweight drift checks for required docs, scripts, and critical paths.**  
  Why: Silent drift breaks trust in guidance and tooling.  
  How: Add automated presence and path checks. Run them in smoke/pre-merge pipelines. Keep the required-file list intentional and reviewed.
- **Keep operational ownership and escalation paths documented.**  
  Why: Unclear ownership delays response during failures.  
  How: Maintain explicit owner mappings per subsystem. Define escalation order and contact points. Review ownership entries during major architecture changes.

### Shared Principles

- **Documentation is an operational dependency, not optional prose.**  
  Why: Operations fail when procedures and architecture are undocumented.  
  How: Treat documentation as part of done criteria. Keep runbooks versioned with code changes. Review docs for operational accuracy, not only grammar.
- **Decision history should be discoverable and auditable.**  
  Why: Traceable context improves long-term maintainability and accountability.  
  How: Keep decision records indexed and linked to changes. Use consistent naming for discoverability. Periodically archive stale records with references, not deletion.
- **Contributor workflows should be deterministic across environments.**  
  Why: Reproducible workflows reduce "works on my machine" failures.  
  How: Standardize command paths and environment variables. Pin defaults where variability creates risk. Validate workflows in fresh environments regularly.
- **Operational readiness must be maintained continuously, not only during incidents.**  
  Why: Reactive preparation increases outage duration and cost.  
  How: Exercise runbooks in normal operations. Verify alert and escalation paths on a schedule. Track readiness gaps as actionable backlog items.
- **Governance should reduce ambiguity, not increase process overhead.**  
  Why: Heavy process without clarity slows teams without improving outcomes.  
  How: Keep controls minimal and risk-based. Remove steps that do not improve decisions. Measure governance quality by clarity and incident outcomes.

## E) Human Governance & Policy Enforcement

### Practices

- **Require explicit human approval for high-impact or irreversible actions.**  
  Why: Irreversible operations need accountable decision ownership.  
  How: Place approval gates before execution. Capture approver identity, context, and rationale. Enforce no-bypass rules in automation paths.
- **Enforce role/policy authorization at execute, approve, and publish boundaries.**  
  Why: Partial enforcement creates exploitable control gaps.  
  How: Apply consistent policy checks at all sensitive transitions. Keep policy evaluation logic centralized. Test allow and deny paths equally.
- **Persist both approvals and denials as auditable events with actor/context metadata.**  
  Why: Complete audit trails are required for compliance, debugging, and trust.  
  How: Log decision events with actor, role, action, and timestamp. Include request context and target resource. Protect audit history from silent mutation.
- **Apply least-privilege defaults and explicit elevation paths.**  
  Why: Over-privileged defaults expand the blast radius of mistakes or compromise.  
  How: Grant minimal rights by default. Require explicit justification for elevation. Time-bound elevated permissions where possible.
- **Re-check permissions on resume/retry/replay paths, not only at initial execution.**  
  Why: Context can change between initial run and continuation flows.  
  How: Re-evaluate authorization whenever control re-enters protected steps. Validate role changes and policy updates before continuing. Record permission re-check outcomes.
- **Validate policy inputs at boundaries to prevent unsafe bypasses.**  
  Why: Malformed or unexpected policy data can disable safeguards silently.  
  How: Enforce strict input schemas for policy payloads. Reject invalid policy data early with explicit errors. Add contract tests for malformed and edge inputs.

### Shared Principles

- **Trust boundaries must be explicit and enforced uniformly.**  
  Why: Inconsistent trust models create unpredictable security posture.  
  How: Define boundary rules once and reuse them across workflows. Validate boundary behavior with tests and audits. Review boundary consistency during architecture changes.
- **Automation should amplify human judgment, not bypass governance.**  
  Why: Automation without oversight can accelerate harmful outcomes.  
  How: Keep humans in key decision loops. Automate evidence collection and recommendation steps. Prevent direct execution when explicit approval is required.
- **Security and governance outcomes must be observable and testable.**  
  Why: Unverified controls provide false confidence.  
  How: Instrument allow/deny outcomes and decision metadata. Add behavior tests for expected control enforcement. Monitor for bypass patterns and policy drift.
- **Denial paths are first-class behavior and must be user-understandable.**  
  Why: Unclear denials cause unsafe retries and support overhead.  
  How: Return explicit denial reasons and remediation hints. Keep wording consistent across interfaces. Test denial UX and operator logs together.
- **Governance must scale without eroding accountability.**  
  Why: Growth often diffuses responsibility unless controls are designed for scale.  
  How: Preserve actor attribution across all sensitive actions. Keep decision lineage queryable as volume grows. Use governance metrics that include accountability coverage.

## F) Data Continuity, Replay & Lineage

### Practices

- **Persist append-only, structured history sufficient for replay/recovery.**  
  Why: Recoverability depends on complete and ordered historical evidence.  
  How: Write immutable event records with stable schema. Include ordering and source metadata on each record. Avoid in-place edits to historical data.
- **Preserve run/version/source identity across pause, resume, replay, and migration flows.**  
  Why: Identity drift breaks traceability and can misapply logic.  
  How: Carry identifiers explicitly in persisted and reconstructed state. Validate identity continuity at each transition. Reject flows with inconsistent lineage.
- **Track derivation lineage between produced artifacts and their parents.**  
  Why: Lineage enables provenance audits and impact analysis of changes.  
  How: Record parent-child links at creation time. Store relation type and context for each link. Index lineage for efficient query and audit use.
- **Keep event/schema envelopes explicit and versioned.**  
  Why: Versioned envelopes allow safe interpretation across evolving producers and consumers.  
  How: Include schema/version keys in every envelope. Validate required keys before processing. Introduce new versions additively and document transition rules.
- **Validate replay data integrity before applying mutations.**  
  Why: Corrupted replay input can cascade into incorrect live state.  
  How: Run integrity checks at replay start. Quarantine or fail fast on corrupted segments by policy. Emit anomalies with enough context for diagnosis.
- **Support deterministic reconstruction from persisted records.**  
  Why: Nondeterministic replay prevents reliable debugging and incident recovery.  
  How: Define deterministic ordering rules. Keep reconstruction functions pure and side-effect controlled. Test repeated replay for identical outcomes.

### Shared Principles

- **Recoverability is a first-class system capability.**  
  Why: Systems must continue operating through interruptions and faults.  
  How: Design replay and resume paths as primary features. Test them as often as normal execution paths. Include recovery criteria in release readiness.
- **Historical fidelity must be preserved across evolution.**  
  Why: Rewriting history breaks audits and invalidates diagnostics.  
  How: Keep historical records immutable. Use additive changes for schema and behavior evolution. Maintain compatibility readers for prior versions when required.
- **Provenance must remain queryable for audit, debugging, and trust.**  
  Why: Opaque provenance blocks root-cause analysis and compliance validation.  
  How: Index lineage and source metadata for query use. Provide standard lookup paths for operators and reviewers. Verify provenance queries in tests.
- **Data continuity requires both durability and interpretability.**  
  Why: Durable bytes alone are useless if they cannot be interpreted later.  
  How: Pair reliable storage with explicit schema evolution rules. Keep migration paths documented and tested. Validate interpretation at read boundaries.
- **Reproducibility underpins operational confidence.**  
  Why: Teams trust systems they can reproduce under pressure.  
  How: Execute deterministic replay tests regularly. Compare outcomes across runs and environments. Treat nondeterminism as a high-priority defect.

## G) Observability & Resilience by Design

### Practices

- **Separate telemetry channels by concern (state, audit, operations/incidents).**  
  Why: Mixed streams make operational analysis slow and noisy.  
  How: Route each event type to a dedicated channel. Assign clear ownership for each channel. Document channel purposes and retention expectations.
- **Record anomalies as structured events, counters, and summaries.**  
  Why: Unstructured logs do not support reliable automation or trend analysis.  
  How: Emit normalized anomaly payloads with stable fields. Maintain counters for high-level monitoring. Publish summaries for quick triage context.
- **Provide explicit fault-handling policies (`skip`, `degrade`, `raise`) and test each mode.**  
  Why: Implicit error handling creates unpredictable runtime behavior.  
  How: Define policies as configuration, not hidden defaults. Test each policy mode with normal and adverse scenarios. Expose active policy state in diagnostics.
- **Emit correlation identifiers to connect runtime, audit, and incident events.**  
  Why: Correlated traces shorten incident triage and root-cause discovery.  
  How: Generate stable IDs at workflow start. Propagate IDs through all logs and events. Verify correlation continuity in integration tests.
- **Add retention/rotation policies for operational data stores.**  
  Why: Unmanaged telemetry growth increases cost and degrades query performance.  
  How: Define lifecycle rules for aging, compaction, and purge. Apply policies per channel based on operational value. Monitor storage growth and tune windows.
- **Track both error outcomes and recovery outcomes in telemetry.**  
  Why: Resilience quality depends on recovery effectiveness, not only failure counts.  
  How: Record retry, fallback, compensation, and restore events. Link recovery events to originating failures. Include recovery KPIs in operational dashboards.

### Shared Principles

- **Observability data should support both diagnosis and prevention.**  
  Why: Reactive observability alone cannot reduce future incidents.  
  How: Design signals for immediate triage and long-term trends. Keep telemetry consistent enough for automation. Review metrics periodically for prevention opportunities.
- **Resilience means controlled behavior under bad inputs, not silent tolerance.**  
  Why: Silent tolerance hides corruption and delays response.  
  How: Handle invalid input via explicit policy paths. Surface outcomes in telemetry and user-facing diagnostics. Continuously test bad-input scenarios.
- **Operational modes must be explicit, configurable, and verifiable.**  
  Why: Hidden modes create surprises during incidents.  
  How: Expose mode settings in configuration and runtime introspection. Enforce safe defaults per environment. Verify each mode through automated tests.
- **Systems should degrade gracefully before failing hard when safe to do so.**  
  Why: Controlled degradation preserves core service under stress.  
  How: Define fallback paths and trigger thresholds. Keep degraded behavior explicit to operators and users. Test degradation and recovery transitions.
- **Signals should be actionable, not merely verbose.**  
  Why: High-volume but low-value telemetry causes alert fatigue and missed incidents.  
  How: Prioritize concise, contextual signals tied to actions. Remove or demote noisy events that add little decision value. Review alert effectiveness as part of operations hygiene.
