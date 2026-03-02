# Refactoring Guardrail

Purpose:
- prevent architecture drift during normal refactors
- make structural quality rules explicit enough for humans and agents to follow
- catch high-signal code-shape problems before they become coupling debt

## What It Enforces

The default refactoring guard checks three generic structural rules:
1. wildcard imports are forbidden
2. upward relative imports beyond the configured limit are forbidden
3. internal dependency cycles inside the root package are forbidden

These rules are intentionally generic and cross-project:
- wildcard imports hide dependency shape
- deep relative imports obscure architectural direction
- cycles make changes harder to reason about and harder to recover safely

## Configuration

Default config file:
- `tools/refactoring_guardrails.yml`

Default policy:
```yaml
include:
  - src
ignore: []
rules:
  ban_wildcard_imports: true
  max_relative_import_level: 1
  detect_internal_cycles: true
  cycle_roots: []
```

Meaning:
- `ban_wildcard_imports`: blocks `from x import *`
- `max_relative_import_level`: limits relative-import depth
- `detect_internal_cycles`: enables cycle detection
- `cycle_roots`: optional explicit package roots; if empty, the guard auto-discovers the single root package under `src/`

## Runtime

Command:
```bash
make refactoring-guard
```

Also included in:
- `make smoke`
- `make governance-check`
- `make check`

## Federated Extension

Central policy runs from `guardrails-architecture` first.
If that passes, projects may add stricter local rules in:
- `project_governance/hooks.py`

Hook name:
- `check_refactoring_guard(repo_root)`

That local hook is additive only.
It must not bypass or weaken the central baseline.

## Why This Matters For Agentic Coding

Refactors are one of the most common agentic failure modes.
Agents tend to optimize for local correctness and can accidentally:
- hide imports behind `*`
- introduce convenience relative imports that blur boundaries
- create cycles while moving code quickly

This guardrail catches those regressions at commit time.

## Relationship To Other Guardrails

- `version-evolution-guardrail.md`: protects explicit version-by-version evolution rules
- `package-boundary-guardrail.md`: protects configured subsystem/package import boundaries
- `federated-governance-hooks.md`: explains how local projects add stricter rules safely
