# py-crystal-seed

**py-crystal-seed** is a professional-grade Python project template designed to provide strong structural defaults for new projects.

It is not just a “hello world” scaffold.
It is a **structural starting point** for projects that value:

* clarity of architecture
* reproducible environments
* predictable tooling
* long-term maintainability

For development workflow, tooling, IDE setup, and CI patterns, see:
➡ **dev-ops/README.md**

---

## What this project is

This repository is a **template project**. It provides:

* A clean `src/`-based package layout
* A working virtual environment setup
* pytest wired correctly (CLI + IDE + CI compatible)
* Ruff linting and formatting checks
* Pyright static type checking
* Optional packaging/publishing pipeline (build, artifact checks, release workflows)
* GitLab tag-based release gates (`.gitlab-ci.yml`: build/sign -> verify -> publish)
* Operations-hardening gate (`make ops-gate`: perf, leak, recovery, observability)
* Version evolution guardrail (facade-only cross-version imports + lower-version core contract stability)
* Refactoring guardrail (wildcard imports, relative import depth, internal cycle detection)
* Release policy + docs-drift governance checks
* Waiver registry governance with explicit expiry/ownership checks
* Editable installs (`pip install -e .`)
* A minimal but real test
* A minimal but real package
* Clear upgrade path toward CI, pre-commit, and automation

You can clone this project and use it as the base for new Python projects.

---

## Project structure

```
py-crystal-seed/
├── pyproject.toml
├── README.md
├── pytest.ini
├── dev-ops/
│   └── README.md
├── src/
│   └── py_crystal_seed/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
└── .gitignore
```

---

## Running the template

After setting up the environment (see `dev-ops/README.md`), you can run:

```bash
python -m py_crystal_seed.main
```

Expected output:

```
The structure holds.
```

Tests can be run with:

```bash
pytest
```

### Quick setup (recommended)

This project includes a small bootstrap script that sets up a complete, correct development environment automatically.

From the project root:

```bash
./scripts/bootstrap.sh
source venv/bin/activate
pytest
```

This script:

* creates the virtual environment
* installs build tooling (pip, setuptools, wheel)
* installs the project in editable mode
* installs development dependencies 

It ensures that everyone starts from the same, working setup.

For details, see: **[scripts/README.md](scripts/README.md)**.

---

## Renaming the project for your own use

This template is designed to be copied and renamed.

If you want to rename the project to:

> py-structural-anchor

Then follow this mapping:

| Concept               | Example                   |
| --------------------- | ------------------------- |
| Repository name       | `py-structural-anchor`          |
| Python package folder | `src/py_structural_anchor/`     |
| Python import path    | `import py_structural_anchor`   |
| pyproject.toml name   | `name = "py-structural-anchor"` |

### Example: renaming from py-crystal-seed

You must update:

#### Folder name

```
src/py_crystal_seed/ → src/py_structural_anchor/
```

#### Imports in tests

```python
from py_crystal_seed.main import greet
```

becomes:

```python
from py_structural_anchor.main import greet
```

#### CLI execution

```bash
python -m py_crystal_seed.main
```

becomes:

```bash
python -m py_structural_anchor.main
```

> Note: Hyphens (`-`) are valid for project names, but **not valid for Python imports**.
> That’s why package folders use underscores.

---

## How this template differs from many Python projects

Most Python repositories evolve organically:

* ad-hoc virtualenvs
* inconsistent imports
* tests added later
* tooling bolted on gradually
* environment instructions scattered across docs
* IDE configuration undocumented

This template takes the opposite approach:

| Common approach                   | This template                         |
| --------------------------------- | ------------------------------------- |
| venv setup is implicit            | venv setup is explicit and documented |
| imports rely on working directory | imports rely on proper packaging      |
| tests optional                    | tests are part of the structure       |
| IDE setup undocumented            | PyCharm + CLI setup documented        |
| packaging later                   | packaging from day one                |
| tooling grows organically         | tooling is intentional from start     |

### Why this adds value

This structure leads to:
* Fewer “works on my machine” issues
* Easier onboarding for new contributors
* Better compatibility with CI/CD systems
* Safer refactoring
* Clearer project boundaries
* A project that scales without structural rewrites

---

## Philosophy

This template favors:

* explicit over implicit
* structure over convenience
* reproducibility over shortcuts
* long-term maintainability over quick starts

It is meant for projects that expect to grow.

### Why we add these extra gates

Some checks can look like overhead until they prevent production pain.

This template separates gates by intent:
- fast developer loop: `make check` (lint, typecheck, tests, architecture guardrails)
- release trust lane: supply-chain + signing + verification gates
- operations-hardening lane: `make ops-gate` (performance, leak, recovery, observability)

This keeps day-to-day iteration fast while still making runtime reliability and release trust explicit and testable.

Local commits use the repo-owned gate in `scripts/run_commit_gate.sh`.
That avoids hidden dependence on a generated `.git/hooks/pre-commit` launcher whose Python environment can drift from the repository contract.

The next recommended wave is governance depth:
- coverage governance
- maturity evidence enforcement
- weekly trend reporting and guard telemetry
- refactoring guard expansion

Roadmap:
- `docs/maturity/roadmap/phase-3-governance-depth-wave.md`

### Maturity model (Java-style analog target)

Documentation and guardrails are organized by four maturity pillars:
1. Build/test/type/lint discipline: ~95%
2. Packaging/distribution discipline: ~94%
3. Governance/auditability discipline: ~93%
4. Supply-chain/operations hardening: ~80%

See unified docs index:
- **[docs/README.md](docs/README.md)**
Live dashboard:
- **[docs/maturity/status-dashboard.md](docs/maturity/status-dashboard.md)**
Reusable adoption mechanism:
- **[docs/maturity/maturity-mechanism.md](docs/maturity/maturity-mechanism.md)**

---

## Development & Tooling

For full instructions on:

* virtual environment setup
* pytest usage
* PyCharm configuration
* editable installs
* CI integration
* pre-commit hooks

See:

See the full development guide in **[dev-ops/README.md](dev-ops/README.md)**.
For Codex/maintainer workflow and template contribution rules, see
**[DEVELOPER_README.md](DEVELOPER_README.md)**.
For packaging and publishing workflow details, see
**[docs/maturity/packaging-distribution/packaging-distribution.md](docs/maturity/packaging-distribution/packaging-distribution.md)**.
For supply-chain and operations hardening controls, see
**[docs/maturity/supply-chain-operations/supply-chain-operations.md](docs/maturity/supply-chain-operations/supply-chain-operations.md)**.
For detailed perf/leak/recovery/observability gate behavior, see
**[docs/maturity/supply-chain-operations/operations-hardening-gates.md](docs/maturity/supply-chain-operations/operations-hardening-gates.md)**.
For version-by-version evolution safety and agentic coding drift prevention, see
**[docs/maturity/governance-auditability/version-evolution-guardrail.md](docs/maturity/governance-auditability/version-evolution-guardrail.md)**.
For package boundary and ADR governance guardrails, see
**[docs/maturity/governance-auditability/package-boundary-guardrail.md](docs/maturity/governance-auditability/package-boundary-guardrail.md)**
and
**[docs/maturity/governance-auditability/adr-quality-guardrail.md](docs/maturity/governance-auditability/adr-quality-guardrail.md)**.
For generic structural refactoring rules, see
**[docs/maturity/governance-auditability/refactoring-guardrail.md](docs/maturity/governance-auditability/refactoring-guardrail.md)**.
Use the default ADR template at
**[docs/adr/ADR-0000-template.md](docs/adr/ADR-0000-template.md)**.
For the lean-template adoption strategy via shared guardrail libraries, see
**[docs/maturity/governance-auditability/guardrail-library-externalization.md](docs/maturity/governance-auditability/guardrail-library-externalization.md)**.
For the canonical packaging and publication model for guardrail libraries, see
**[docs/maturity/governance-auditability/guardrail-packaging-model.md](docs/maturity/governance-auditability/guardrail-packaging-model.md)**.
For the target enforcement matrix for commits, CI, releases, and weekly reporting, see
**[docs/maturity/governance-auditability/commit-lockdown-strategy.md](docs/maturity/governance-auditability/commit-lockdown-strategy.md)**.
For the declarative config and result-envelope contract, see
**[docs/maturity/governance-auditability/guardrail-manifest-contract.md](docs/maturity/governance-auditability/guardrail-manifest-contract.md)**.
For how downstream projects should consume published guardrails, see
**[docs/maturity/governance-auditability/downstream-guardrail-consumption.md](docs/maturity/governance-auditability/downstream-guardrail-consumption.md)**.
For the central-plus-local governance extension model, see
**[docs/maturity/governance-auditability/federated-governance-hooks.md](docs/maturity/governance-auditability/federated-governance-hooks.md)**.
For the full guardrail map, see
**[docs/maturity/governance-auditability/guardrails-index.md](docs/maturity/governance-auditability/guardrails-index.md)**.
Core guardrail docs:
- **[Operations hardening guardrail](docs/maturity/supply-chain-operations/operations-hardening-guardrail.md)**
- **[Supply-chain and release trust guardrail](docs/maturity/supply-chain-operations/supply-chain-release-trust-guardrail.md)**
- **[Release policy guardrail](docs/maturity/governance-auditability/release-policy-guardrail.md)**
- **[Documentation drift guardrail](docs/maturity/governance-auditability/docs-drift-guardrail.md)**
- **[Waiver governance guardrail](docs/maturity/governance-auditability/waiver-governance-guardrail.md)**
- **[Package boundary guardrail](docs/maturity/governance-auditability/package-boundary-guardrail.md)**
- **[Refactoring guardrail](docs/maturity/governance-auditability/refactoring-guardrail.md)**
- **[ADR quality guardrail](docs/maturity/governance-auditability/adr-quality-guardrail.md)**
- **[Guardrail library externalization](docs/maturity/governance-auditability/guardrail-library-externalization.md)**
- **[Guardrail packaging model](docs/maturity/governance-auditability/guardrail-packaging-model.md)**
- **[Commit lockdown strategy](docs/maturity/governance-auditability/commit-lockdown-strategy.md)**
- **[Guardrail manifest contract](docs/maturity/governance-auditability/guardrail-manifest-contract.md)**
- **[Downstream guardrail consumption](docs/maturity/governance-auditability/downstream-guardrail-consumption.md)**
- **[Federated governance hooks](docs/maturity/governance-auditability/federated-governance-hooks.md)**
- **[Maturity mechanism guardrail](docs/maturity/governance-auditability/maturity-mechanism-guardrail.md)**
For release promotion and rollback steps, see
**[RELEASING.md](RELEASING.md)**.

---

## Future extensions

This template intentionally provides a strong foundation without imposing heavy tooling.
Depending on your project’s maturity, you may consider extending it with:

- domain-specific package boundary rules in `tools/package_boundaries.yml`
- ADR workflows (decision templates + review automation) for architecture-heavy teams
- extraction of local guardrail internals into shared versioned libraries
- package CLI publication with manifest-driven policy contracts
- full-governance commit blocking and weekly governance reporting
- stronger runtime SLI gates and trend dashboards on top of `make ops-gate`
- automated release-note/changelog generation with approval controls

The structure of this template is designed to support these additions without requiring restructuring.
