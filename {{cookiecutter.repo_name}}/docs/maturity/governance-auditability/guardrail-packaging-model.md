# Guardrail Packaging Model

Purpose:
- define the canonical packaging model for all `guardrails-*` libraries
- keep the template lean while making governance reusable across repositories
- ensure future extraction/publication follows one stable contract

## Problem Statement

Raw scripts and repo-relative logic are the wrong long-term public surface.
They drift when copied, assume local filesystem structure, and make cross-project upgrades expensive.

Published Python libraries are the target contract because they provide:
- stable Python APIs
- stable CLI entrypoints
- packaged schemas/templates/defaults
- versioned release semantics
- predictable installation in CI and local development

## Canonical Architecture

Each `guardrails-*` package should use the same internal structure:
- `core logic`: actual validation/execution engine
- `config loader`: reads repo-local YAML/JSON/Markdown-backed policy inputs
- `schema validator`: validates manifests and guard-specific configs
- `cli`: stable command-line interface for downstream repos and CI
- `resources`: package data such as defaults, schemas, templates, and examples
- `result model`: shared output envelope for human and machine consumers
- `tests`: package-level unit and integration coverage

Recommended layout:

```text
guardrails-governance/
  pyproject.toml
  src/
    guardrails_governance/
      __init__.py
      cli.py
      adr_quality.py
      docs_drift.py
      waivers.py
      result.py
      resources/
        templates/
          adr_template.md
        schemas/
          docs_drift.schema.json
        defaults/
          docs_drift.defaults.yml
  tests/
```

Use the same pattern for:
- `guardrails-architecture`
- `guardrails-release`
- `guardrails-ops`

## Public Surface

Normative rules:
- CLI entrypoints are exposed via `[project.scripts]` or equivalent `console_scripts`
- bundled assets are accessed with `importlib.resources`
- repo-relative fallback paths are forbidden inside published library code
- each central guard must be callable from both Python and CLI
- JSON output mode is part of the stable contract

### Python API examples

- `guardrails_governance.adr_quality.run_adr_quality_check`
- `guardrails_governance.docs_drift.run_docs_drift_check`
- `guardrails_governance.waivers.run_waiver_check`
- `guardrails_architecture.version_evolution.run_version_evolution_check`
- `guardrails_architecture.package_boundaries.run_package_boundary_check`
- `guardrails_architecture.refactoring_guard.run_refactoring_guard_check`
- `guardrails_release.release_policy.run_release_policy_check`
- `guardrails_ops.ops.run_ops_gates`

### CLI entrypoints

Canonical commands:
- `guardrails-check-adr`
- `guardrails-check-docs-drift`
- `guardrails-check-waivers`
- `guardrails-check-version-evolution`
- `guardrails-check-package-boundaries`
- `guardrails-check-refactoring`
- `guardrails-check-release-policy`
- `guardrails-run-ops-gates`

Future commands:
- `guardrails-check-coverage-governance`
- `guardrails-check-maturity-evidence`
- `guardrails-report-weekly`

### CLI argument contract

Each CLI should converge on:
- `--repo-root`
- `--config` where relevant
- `--output text|json`
- guard-specific flags only where unavoidable

## What Stays Central vs Local

Central package responsibilities:
- guard engine logic
- defaults
- schemas
- templates
- examples
- Python API
- CLI entrypoints
- result model

Consuming repo responsibilities:
- repo-local manifests
- policy exceptions and waivers
- optional additive local hooks
- CI wiring and wrapper ergonomics

## Result Model

Every guard should support:
- human-readable text output by default
- machine-readable JSON via `--output json`

Canonical JSON envelope:

```json
{
  "guard": "refactoring_guard",
  "status": "pass",
  "violations": [],
  "warnings": [],
  "metrics": {},
  "advice": []
}
```

Failure output keeps the same shape, with:
- `status: fail`
- `violations`: typed findings
- `metrics`: optional counts/timings
- `advice`: remediation hints

## Semantic Versioning Policy

Use SemVer per guardrail package:
- patch: bugfix in existing rule behavior or packaging
- minor: additive checks, additive CLI options, non-breaking manifest/schema additions
- major: changed policy semantics, changed CLI/API contract, required config migration

## Bash Policy

Bash is orchestration only.
Use shell for:
- convenience scripts in template repos
- CI glue
- wrapper orchestration

Do not use shell as the primary reusable public surface.
The reusable contract is:
- Python API
- CLI entrypoint
- packaged resources

## Internal-First Publication

Initial target:
- internal PyPI-compatible package index first

Later option:
- public PyPI if distribution scope justifies it

Downstream repos should depend on versions, not copied scripts or directories.
The maturity upgrade path is dependency bumping plus manifest/local-hook review.

## Related Docs

- `guardrail-library-externalization.md`
- `guardrail-manifest-contract.md`
- `downstream-guardrail-consumption.md`
- `federated-governance-hooks.md`
