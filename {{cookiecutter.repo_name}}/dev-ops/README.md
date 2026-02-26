# Development & Tooling Guide

This document describes the development workflow and tooling for this project. It is intended for contributors and maintainers who want a reliable, repeatable setup across local development, IDEs, and CI environments.

---

## Project Layout

```
py-crystal-seed/
├── src/
│   └── py_crystal_seed/
│       ├── __init__.py
│       ├── main.py
├── tests/
│   └── test_main.py
├── pytest.ini
├── pyproject.toml
├── README.md
├── .gitignore
└── .venv/               # local virtualenv (not committed)
```

The `src/` layout prevents accidental imports from the project root and mirrors real-world packaging practices.

---

## Python Version

This project targets:

> Python ≥ 3.10 (3.11 or 3.12 recommended)

Check your version with:

```bash
python -V
```

---

## Setting up a local python environment

From the project root:

```bash
# Remove any existing environment (optional but recommended if broken)
rm -rf venv

# Create a fresh virtual environment with Python 3.12
python3.12 -m venv venv

# Upgrade pip inside the venv
./venv/bin/python -m pip install -U pip

# Verify interpreter version
./venv/bin/python -V

# Install project in editable mode
./venv/bin/python -m pip install -e .

# Install dev dependencies (pytest, ruff, pyright, pre-commit)
./venv/bin/python -m pip install -e '.[dev]'
```

You should now be able to run tests from this environment.

---

## Running tests

### CLI

From project root:

```bash
source venv/bin/activate
pytest -q
```

If you want to be explicit:

```bash
python -m pytest -q
```

### PyCharm (configure a pytest run config)

1. Run → Edit Configurations…
2. Click **+**
3. Choose **Python tests → pytest**
4. Target:

   * `tests/` (folder), or
   * `tests/test_main.py` (file)
5. Working directory: project root (`.../py-cyrstal-seed`)
6. Interpreter: your venv (`.../venv/bin/python`)
7. Apply → Run

If PyCharm doesn’t show “pytest” as an option, enable it:

* Settings → Tools → Python Integrated Tools → Default test runner: **pytest**
* Or install pytest in the venv first (`pip install pytest`)

---

You should now be able to run:

```bash
pytest
```

---

## Quality gates with pre-commit

This project uses `pre-commit` to ensure that commits do not introduce quality regressions.

The pre-commit hooks run:

```bash
./scripts/lint.sh
./scripts/typecheck.sh
./tools/check_version_import_boundaries.py
./scripts/test.sh
```

### Setup

Install development dependencies:

```bash
pip install -e '.[dev]'
```

Install the git hook:

```bash
pre-commit install
```

### What happens on commit?

On every git commit:
- Ruff lint and format checks are executed
- Pyright type checks are executed
- version import-boundary checks are executed
- the test suite is executed
- if any check fails, the commit is blocked

This ensures style, type safety, and behavior stay healthy before code is committed.

### Run manually

You can run the same checks manually at any time:

```bash
./scripts/lint.sh
./scripts/typecheck.sh
./venv/bin/python ./tools/check_version_import_boundaries.py
./scripts/test.sh
```

Notice:
- dev-ops doc talks about **process and intent**
- scripts doc talks about **mechanics**
- bootstrap remains untouched
- responsibilities are cleanly separated

---

## Why editable install?

We use:

```bash
pip install -e .
```

This ensures:

* `py_crystal_seed` is importable everywhere
* imports behave consistently in CLI, PyCharm, and CI
* changes to source code are reflected immediately without reinstalling

This is the standard workflow for professional Python projects.

---

## Running Tests

### Command Line

```bash
pytest
```

or explicitly:

```bash
python -m pytest
```

### PyCharm

Configure pytest as the test runner:

1. Settings → Tools → Python Integrated Tools
2. Set Default test runner = pytest

Then:

* Right click `tests/` → Run pytest
* Or right click individual test files

Ensure the project interpreter points to `.venv/bin/python`.

---

## pytest configuration

This project uses a simple `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

This guarantees consistent discovery across environments.

---

## Development dependencies

You may optionally formalize dev tools in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "pyright",
    "pre-commit",
]
```

Then install with:

```bash
pip install -e '.[dev]'
```

---

## Continuous Testing Philosophy

Python has no traditional "compile-time", so correctness is enforced through:

* Ruff + Pyright (local static analysis)
* pytest (local runs)
* IDE test runner (PyCharm)
* CI pipelines (e.g. GitHub Actions)
* pre-commit hooks

This ensures tests fail fast when behavior regresses.

---

## Packaging & Distribution (Optional Lane)

Packaging and publishing are intentionally separated from the default development lane.

Use:

```bash
make package-build
make package-check
make package-install
```

Publish commands:

```bash
make package-publish-test   # requires TEST_PYPI_API_TOKEN
make package-publish        # requires PYPI_API_TOKEN
```

CI workflows:
- `package-validation.yml` validates build artifacts on push/PR
- `publish-testpypi.yml` publishes to TestPyPI (manual)
- `publish-pypi.yml` publishes to PyPI (manual or release)

---

## Optional: Pre-commit hook (recommended)

To run tests automatically before every commit, create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: pytest
        language: system
        pass_filenames: false
```

Then install:

```bash
pip install pre-commit
pre-commit install
```

Now every `git commit` runs the test suite.

---

## Optional: CI example (GitHub Actions)

```yaml
name: tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -e '.[dev]'
      - run: pytest
```

---

## Common Issues

### Imports fail (`ModuleNotFoundError: py_crystal_seed`)

Solution:

* Ensure you ran `pip install -e .`
* Ensure PyCharm interpreter is `.venv/bin/python`

### Tests show “Ran 0 tests”

Cause:

* You are running `unittest` instead of `pytest`

Solution:

* Use pytest runner in PyCharm
* Run `pytest` from CLI

---

## Recommended workflow

Daily development loop:

```bash
source .venv/bin/activate
pytest
# write code
pytest
# commit
```

IDE workflow:

* PyCharm interpreter → `.venv`
* Run pytest via right click
* Optional: enable pre-commit

---

## Philosophy

The tooling choices here favor:

* clarity over cleverness
* explicitness over magic
* reproducibility over convenience
* extensibility over shortcuts

The goal is that anyone cloning this project can run:

```bash
python -m venv .venv
pip install -e '.[dev]'
pytest
```

…and immediately have a working development environment.
