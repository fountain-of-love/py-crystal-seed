# Developer README (Codex-Focused)

This guide explains how to work in `py-crystal-seed` as a maintainer or AI coding agent.

The goal of this repository is to encode good engineering defaults early:
- reproducible environment setup
- deterministic quality gates
- consistent project generation via Cookiecutter
- clear path from seed project to generated production repo

## What This Repository Contains

This repo has two roles:

1. Seed project (real, runnable):
- `src/py_crystal_seed/`
- `tests/`
- root `pyproject.toml`, `Makefile`, scripts, CI

2. Cookiecutter template blueprint:
- `{{cookiecutter.repo_name}}/` (templated project output)
- `cookiecutter.json` (prompt variables)
- `hooks/post_gen_project.py` (safe inject behavior)

If you change engineering defaults, update both seed and template unless intentionally scoped.

## Core Engineering Defaults

Quality gates are first-class and should stay green:
- Ruff for lint + format
- Pyright for static typing (strict mode)
- Pytest for behavior
- Pre-commit for local gate enforcement
- GitHub Actions for CI gate enforcement

Canonical commands:

```bash
make setup      # bootstrap env + install dev deps + install pre-commit
make smoke      # lint + typecheck + tests + version import-boundary guard
make lint       # ruff check + format check
make format     # ruff autofix + format
make typecheck  # pyright
make test       # pytest
make check      # full local gate (smoke + pre-commit)
make package-build   # build wheel + sdist
make package-check   # validate package metadata
make package-install # install built wheel locally
make docs-drift      # enforce docs drift policy
make release-policy  # enforce SemVer/tag/changelog policy
make release-ready   # run full release readiness gate
```

## How to Generate Projects from This Template

### Greenfield generation

```bash
make new OUT=/path/to/parent/dir
```

### Safe generation without overwrite

```bash
make apply-safe TARGET=/path/to/parent/dir
```

### Inject into an existing repo (explicit only)

```bash
make inject TARGET=/path/to/existing/repo
```

Injection rules are controlled by `hooks/post_gen_project.py` and env vars:
- `CC_INJECT=1` required
- `CC_OVERWRITE` allowlists top-level paths that may be overwritten
- `CC_MANUAL_MERGE` protects merge-sensitive files
- `CC_PROTECT` protects top-level code paths like `src/` and `tests/`

## Rules for Contributors and AI Agents

- Keep quality gates deterministic; do not bypass `scripts/*.sh` entrypoints.
- Prefer updating scripts/Makefile/CI together when changing tooling.
- Keep docs in sync with behavior (`README.md`, `dev-ops/README.md`, `scripts/README.md`, template docs).
- Do not introduce direct edits that break Cookiecutter placeholders in templated files.
- Validate with `make check` before finalizing substantial changes.

## Abstract Evolutionary Architecture Policy

Use this policy for projects generated from this template when they evolve in versions
(for example `v1`, `v2`, `v3`) or compatibility layers.

### 1) Boundaries Must Stay Explicit

- Each version keeps a clear public facade (`.../versions/vN/...` or equivalent).
- Version-specific behavior stays inside that version boundary.
- New version behavior is added by extension/composition, not by retrofitting old semantics.

### 2) Shared Core Holds Mechanism, Not Version Semantics

- Shared core modules contain reusable mechanism only.
- Core naming and contracts must remain version-agnostic.
- Business decisions tied to a specific version belong in that version layer.

### 3) Compatibility Rule (Hard Rule)

If version `N-1` depends on a core API, treat that API as stable for version `N`.

Allowed in `N`:
- subclass and override extension hooks
- wrap/adapt with composition
- add new non-breaking core capabilities

Not allowed in `N`:
- modify core behavior relied on by `N-1`
- remove/rename core symbols used by `N-1`
- change contracts in ways that force `N-1` rewrites

### 4) Cross-Version Import Rule

Allowed:
- `vN -> core.*`
- `vN -> facade of v(N-1)` (when evolutionary chaining is intentional)

Forbidden:
- `vN -> internal modules of v(N-1)`

Keep imports facade-only across versions to preserve encapsulation and replaceability.

### 5) Refactoring Workflow Per Version

1. Identify duplication in `vN`.
2. Classify duplicated logic:
   - shared mechanism -> candidate for core
   - version semantics -> keep in version
3. If extracting to core:
   - add new core module/class in backward-compatible form
   - adapt `vN` via extension/composition
   - keep existing facades stable
4. Validate no forbidden cross-version internal imports.
5. Run full quality and feature test suite.
6. Update version docs + migration notes.

### 6) PR Review Gate (Architecture)

- [ ] No imports from older-version internals (facade-only respected)
- [ ] Core changes are additive or backward-compatible
- [ ] No behavior drift in older-version tests
- [ ] New behavior implemented via extension/composition
- [ ] Public facade stability preserved (or explicitly versioned)
- [ ] Docs/migration notes updated

### 7) Anti-Patterns to Avoid

- Fixing old-version behavior by mutating shared core behavior in-place.
- Importing convenient internals across version boundaries.
- Moving version semantics into core only to reduce duplication.
- Collapsing version facades and losing explicit evolution narrative.

### 8) Versioned Project Skeleton (Reference)

Use this as a generic baseline for versioned systems:

```text
project/
├── src/project_name/
│   ├── core/
│   │   ├── contracts.py
│   │   ├── models.py
│   │   └── services.py
│   └── versions/
│       ├── v1/
│       │   ├── facade.py
│       │   ├── policies.py
│       │   └── adapters.py
│       ├── v2/
│       │   ├── facade.py
│       │   ├── policies.py
│       │   └── adapters.py
│       └── v3/
│           ├── facade.py
│           ├── policies.py
│           └── adapters.py
├── tests/
│   ├── core/
│   └── versions/
│       ├── v1/
│       ├── v2/
│       └── v3/
└── docs/
    └── versions/
        ├── v1.md
        ├── v2.md
        └── v3.md
```

Dependency direction:
- `versions/vN/* -> core/*`
- `versions/vN/* -> versions/v(N-1)/facade.py` (optional, narrative chaining only)
- never `versions/vN/* -> versions/v(N-1)/*` internals

## When Adding New Functionality

Apply the project’s engineering philosophy from `AGENTS.md`:
- modularity and readability first
- iterative, safe changes
- explicit boundaries
- right-sized complexity
- observable and secure defaults

After implementing new functionality:
1. run quality gates
2. evaluate touched files for refactoring opportunities
3. keep seed and template aligned where applicable

## Fast Sanity Checklist

Before proposing completion:
- `make check` passes locally
- docs reflect actual commands and tooling
- both root project and `{{cookiecutter.repo_name}}/` template are updated
- no accidental regressions in bootstrap/generation flow

## PR Review Checklist

For cross-project PR review standards, use:
- `PR_REVIEW_CHECKLIST.md`

## Engineering Practices

For reusable engineering standards across projects, use:
- `ENGINEERING_PRACTICES.md`
