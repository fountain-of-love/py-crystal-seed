
# Scripts

This folder contains helper scripts that make working with the project **deterministic and repeatable**.

The goal is to ensure that:

* everyone sets up the environment the same way
* tooling behaves consistently across machines
* onboarding is fast and low-friction
* CI can reuse the same commands as local development

These scripts are intentionally simple and transparent.

---

## `bootstrap.sh`

Bootstraps a complete local development environment from scratch.

It performs the following steps:

* creates a fresh virtual environment (`venv/`)
* upgrades core build tooling (`pip`, `setuptools`, `wheel`)
* installs the project in editable mode
* installs development dependencies (e.g. `pytest`)

### Usage

From the project root:

```bash
./scripts/bootstrap.sh
```

Then activate the environment:

```bash
source venv/bin/activate
```

Run tests:

```bash
pytest
```

---

## Philosophy

These scripts are not meant to hide complexity.
They exist to **encode the correct order of operations** so contributors do not have to remember it.

They act as executable documentation for how the project is meant to be used.

---

Potential next steps you can help to add:

* `test.sh` (runs tests with the correct interpreter)
* `lint.sh` (ruff / formatting)
* `typecheck.sh` (pyright / mypy)
* and wire all of them into pre-commit and CI so everything runs from one consistent toolchain
