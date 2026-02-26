# Releasing Guide

This project uses a dedicated packaging lane separate from default development checks.

## Preconditions

Before any release:

1. Run local quality gates:
   - `make check`
2. Build and validate artifacts:
   - `make package-build`
   - `make package-check`
3. Confirm docs/migration notes are updated for user-visible changes.

## Trusted Publishing Setup (One-Time)

In PyPI/TestPyPI, configure this repository as a Trusted Publisher for:

- `publish-testpypi.yml` (environment: `testpypi`)
- `publish-pypi.yml` (environment: `pypi`)

In GitHub:

- protect environment `testpypi` as needed
- protect environment `pypi` with required reviewers

## Promotion Flow

### Step 1: Publish to TestPyPI

Run workflow:
- `.github/workflows/publish-testpypi.yml`

Then verify in a fresh environment:

```bash
python -m venv /tmp/release-check-venv
source /tmp/release-check-venv/bin/activate
python -m pip install -U pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple {{cookiecutter.repo_name}}==<version>
python -c "import {{cookiecutter.package_name}}; print({{cookiecutter.package_name}}.__name__)"
```

### Step 2: Publish to PyPI

Run workflow:
- `.github/workflows/publish-pypi.yml`

Trigger options:
- manual (`workflow_dispatch`)
- publish a GitHub release

### Step 3: Post-Release Verification

Verify install from PyPI:

```bash
python -m venv /tmp/release-prod-check-venv
source /tmp/release-prod-check-venv/bin/activate
python -m pip install -U pip
python -m pip install {{cookiecutter.repo_name}}==<version>
python -c "import {{cookiecutter.package_name}}; print({{cookiecutter.package_name}}.__name__)"
```

## Rollback / Recovery

Python package versions are immutable on PyPI. If a bad release is published:

1. Do not attempt overwrite.
2. Yank the bad version on PyPI.
3. Prepare a fixed patch version.
4. Re-run the same promotion flow (TestPyPI -> PyPI).
5. Document incident and remediation in release notes.
