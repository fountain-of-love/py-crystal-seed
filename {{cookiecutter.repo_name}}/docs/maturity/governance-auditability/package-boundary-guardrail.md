# Package Boundary Guardrail

Purpose:
- enforce explicit dependency direction between top-level packages/subsystems
- prevent accidental cross-domain coupling during human and agentic changes

## Why this exists

As projects grow, package-level boundaries become implicit and easy to violate.
This guardrail makes these rules executable so architecture intent remains stable over time.

## Enforcement

- Tool: `tools/check_package_boundaries.py`
- Config: `tools/package_boundaries.yml`
- Runtime: included in `make smoke` and `make governance-check`

## Policy Model

Rules are config-driven.
Each rule defines:
- `package`: package to validate
- `forbidden_prefixes`: import roots the package must not import

Example:

```yaml
rules:
  - package: app.runtime
    forbidden_prefixes:
      - app.research
  - package: app.research
    forbidden_prefixes:
      - app.runtime
```

## Commands

```bash
make package-boundaries-check
make smoke
```

## Externalization Path

Keep this command stable while moving rule evaluation internals into a shared guardrail library later.
Downstream projects then adopt stronger policy behavior by bumping dependency version, without changing CI command wiring.
