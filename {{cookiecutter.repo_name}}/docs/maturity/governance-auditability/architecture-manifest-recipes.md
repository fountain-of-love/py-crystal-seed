# Architecture Manifest Recipes

Purpose:
- show how to use `tools/refactoring_guardrails.yml` for stronger structure rules

## Directional Dependency Rule

```yaml
rules:
  directional_dependencies:
    - from: demo_pkg.presentation
      may_import:
        - demo_pkg.business
```

Meaning:
- modules under `demo_pkg.presentation` may import `demo_pkg.business`
- imports outside that allowed set are flagged

## Concrete Import Restriction

```yaml
rules:
  forbid_concrete_imports:
    - scope: demo_pkg.business
      forbidden_prefixes:
        - demo_pkg.persistence.http
```

Meaning:
- business-layer code may not import concrete persistence HTTP modules directly

## Composition-Root Allowlist

```yaml
rules:
  allow_concrete_wiring_only_in:
    - demo_pkg.composition_root
```

Meaning:
- concrete wiring is only allowed in the configured composition root
- other scopes must depend on abstractions and approved boundaries
