# ADR Quality Guardrail

Purpose:
- keep architecture decisions explicit, reviewable, and auditable
- enforce a consistent ADR structure across contributors and agents

## Why this exists

Governance quality decays when architectural decisions are undocumented or inconsistent.
This guardrail turns decision-recording into an executable policy.

## Enforcement

- Tool: `tools/check_adr_quality.py`
- ADR location: `docs/adr/` (or `ADR_DIR` override)
- Runtime: included in `make smoke` and `make governance-check`

## Required ADR Standard

Each ADR must include:
- canonical filename (`ADR-0001-title.md`)
- title and metadata (`Status`, `Date`, `Decision owners`)
- required sections (`Context`, `Decision`, `Alternatives Considered`, `Consequences`, `Validation Evidence`, `Related Docs`)
- at least two numbered alternatives
- explicit consequence markers (`Positive:` and `Tradeoff:`)

## Commands

```bash
make adr-check
make smoke
```

## Externalization Path

Treat this checker as a stable CLI facade.
When extracted to a shared governance library, keep command and policy contract stable so downstream adoption is a dependency update, not a local rewrite.
