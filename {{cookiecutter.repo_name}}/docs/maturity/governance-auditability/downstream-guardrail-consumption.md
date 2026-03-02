# Downstream Guardrail Consumption

Purpose:
- show exactly how a derived project should consume published guardrails
- define the recommended contract for pre-commit, GitLab CI, local workflows, and federated local extensions
- make internal package distribution the default adoption model

## Dependency Model

Initial target: internal PyPI-compatible package index.

Recommended dependency shape:

```toml
[project.optional-dependencies]
dev = [
  "guardrails-governance>=0.1.0,<0.2.0",
  "guardrails-release>=0.1.0,<0.2.0",
  "guardrails-architecture>=0.1.0,<0.2.0",
  "guardrails-ops>=0.1.0,<0.2.0",
]
```

Projects should upgrade governance primarily by bumping these versions.

## Pre-Commit Consumption

Use CLI entrypoints, not shell-first wrappers, as the long-term contract.

Example:

```yaml
repos:
  - repo: local
    hooks:
      - id: guardrails-version-evolution
        name: Guardrails version evolution
        entry: guardrails-check-version-evolution
        language: system
        pass_filenames: false

      - id: guardrails-package-boundaries
        name: Guardrails package boundaries
        entry: guardrails-check-package-boundaries --config tools/package_boundaries.yml
        language: system
        pass_filenames: false

      - id: guardrails-refactoring
        name: Guardrails refactoring
        entry: guardrails-check-refactoring --config tools/refactoring_guardrails.yml
        language: system
        pass_filenames: false
```

Extend the same pattern for:
- ADR quality
- docs drift
- waivers
- release policy

## GitLab CI Consumption

Recommended jobs:
- `quality_governance`
- `ops_gates`
- `weekly_governance_report`
- release jobs

Expected behavior:
- merge requests and branch pipelines run `make smoke`, `make governance-check`, and `make ops-gate`
- release/tag jobs run release trust and publish gates
- weekly schedule emits a governance report artifact even when clean

## Thin Wrapper Guidance

Downstream repos may keep thin wrappers for ergonomics, but wrappers are not the primary contract.
Preferred long-term contract:
- Python package dependency
- CLI entrypoint invocation
- repo-local manifest inputs

Wrappers should remain:
- thin
- stable
- free of policy logic

## Local Extension Example

Projects may extend policy in:
- `project_governance/hooks.py`

Example additive hook use cases:
- stricter package boundaries for a domain split
- mandatory ADR owner categories for regulated components
- extra waiver ownership rules for production-critical services

Rules:
- local hooks run only after the central check passes
- local hooks may tighten policy
- local hooks may not bypass central failures

## Upgrade Workflow

Recommended workflow:
1. bump `guardrails-*` package versions
2. run full governance locally and in CI
3. review release notes and migration notes
4. update manifests if required by minor or major changes
5. keep local hooks narrow and additive

## Public Consumption Contract

Downstream repos should rely on:
- Python API for embedding/tests
- CLI commands for CI and pre-commit
- repo-local manifests for policy inputs
- local hooks for project-specific additions

They should not rely on:
- raw shell scripts as the main interface
- absolute paths
- repo-relative assumptions inside shared libraries
- hidden templates outside the wheel/sdist
- py-crystal-seed-specific implementation details

## Acceptance Criteria

- a downstream repo can adopt the model without reading internal implementation code
- internal package index distribution is documented as the default first step
- pre-commit, CI, and local-hook usage are decision complete

## Related Docs

- `guardrail-packaging-model.md`
- `guardrail-manifest-contract.md`
- `commit-lockdown-strategy.md`
