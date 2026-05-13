# Governance Log Contract

Purpose:
- define the minimal structure for machine-checkable governance evidence entries

## File

- `governance/governance_log.yml`

## Shape

```yaml
version: 1
entries:
  - id: GOV-0001
    date: 2026-03-02
    scope:
      - src/py_crystal_seed/example.py
    evidence:
      type: adr
      ref: docs/adr/ADR-0002-sample.md
    summary: Explain why this production change is governed.
    owner: Platform Team
```

## Required Fields

- `id`
- `date`
- `scope`
- `evidence.type`
- `evidence.ref`
- `summary`
- `owner`

## Validation Rule

A governance-log entry only satisfies the maturity-evidence guard when its `scope` covers at least one changed production path.
