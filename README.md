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

---

## Future extensions

This template intentionally provides a strong foundation without imposing heavy tooling.
Depending on your project’s maturity, you may consider extending it with:

- static analysis (ruff, pyright)
- richer typing practices
- automated versioning and release workflows
- extended CI (linting, type checks, coverage)
- documentation tooling (MkDocs, Sphinx)
- packaging and publishing practices

The structure of this template is designed to support these additions without requiring restructuring.
