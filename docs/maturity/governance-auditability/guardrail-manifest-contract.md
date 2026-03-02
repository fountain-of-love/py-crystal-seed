# Guardrail Manifest Contract

Purpose:
- define the declarative manifest model for all guardrail packages
- keep project policy local while central guard engines remain versioned and reusable
- standardize config ownership, path resolution, schema validation, and output behavior

## Principles

- manifests are repo-local
- schemas, defaults, and templates are package-owned
- manifests define policy inputs, not engine logic
- local hooks are additive escape hatches, not the main path
- config contracts should be explicit, versionable, and machine-validatable

## Manifest Inventory By Package

### `guardrails-architecture`

Current local manifests:
- `tools/package_boundaries.yml`
- `tools/refactoring_guardrails.yml`

Future local manifests:
- `tools/directional_dependency_rules.yml`
- `tools/composition_wiring_rules.yml`

### `guardrails-governance`

Current local manifests:
- `waivers/waivers.yml`

Future local manifests:
- `tools/docs_drift.yml`
- `tools/adr_quality.yml`
- `governance/maturity_evidence.yml`

### `guardrails-release`

Future local manifests:
- `tools/release_policy.yml`
- `tools/publish_policy.yml`

### `guardrails-ops`

Future local manifests:
- `tools/ops_gate_policy.yml`
- `tools/weekly_reporting.yml`

## Schema Contract

Each manifest-capable guard should define:
- schema version field where useful
- required keys
- default resolution order
- JSON schema shipped in package data
- example config shipped in package data

Normative rules:
- consuming repos own their manifests
- libraries own the schema and default examples
- invalid manifests fail with explicit diagnostics
- missing manifests use package default behavior only where documented

## Path Resolution Rules

Library code must:
- accept explicit `--config`
- load the documented default repo-local path when `--config` is omitted
- document defaults per guard
- avoid hidden absolute-path or repo-layout assumptions

Target default path model:
- repo-local config path is the public policy location
- packaged default/example resources remain reference assets, not hidden runtime dependencies

## Result Envelope Contract

Every guard CLI should support:
- human-readable text output by default
- machine-readable JSON via `--output json`

Canonical JSON shape:

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

For failures:
- `status`: `fail`
- `violations`: typed findings
- `warnings`: optional non-blocking findings
- `metrics`: optional performance/count values
- `advice`: remediation guidance

## Local Hook Contract

Local hooks are additive only.
Execution order:
1. central engine runs first
2. local hook runs second only if central passed
3. local hook may fail the command
4. local hook may not suppress central failure

Preferred location:
- `project_governance/hooks.py`

Preferred usage:
- use local hooks for domain-specific additions
- prefer manifests/config over hook code where policy is declarative

## Ownership Model

Package provides:
- engine
- defaults
- schemas
- templates
- examples
- CLI
- result contract

Repo provides:
- config manifests
- policy exceptions
- waivers
- local hook behavior
- CI wiring

## Acceptance Criteria

- consuming repos know which files they own
- guard packages know which schemas/defaults they must ship
- config resolution order is defined
- manifest validation failures are explicit and actionable

## Related Docs

- `guardrail-packaging-model.md`
- `downstream-guardrail-consumption.md`
- `federated-governance-hooks.md`
