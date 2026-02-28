# Releasing Guide

This project uses a dedicated packaging lane separate from default development checks.

## Preconditions

Before any release:

1. Run local quality gates:
   - `make check`
2. Build and validate artifacts:
   - `make package-build`
   - `make package-check`
3. Verify Sigstore bundles when validating signed artifacts locally:
   - `SIGSTORE_CERT_IDENTITY="<workflow-identity>" make verify-signatures`
4. Confirm docs/migration notes are updated for user-visible changes.

## Trusted Publishing Setup (One-Time)

In PyPI/TestPyPI, configure this repository as a Trusted Publisher for:

- `publish-testpypi.yml` (environment: `testpypi`)
- `publish-pypi.yml` (environment: `pypi`)

In GitHub:

- protect environment `testpypi` as needed
- protect environment `pypi` with required reviewers

For GitLab pipelines (`.gitlab-ci.yml`):
- set `SIGSTORE_CERT_IDENTITY` in CI/CD variables
- optionally set `SIGSTORE_OIDC_ISSUER` (default `https://gitlab.com`)
- set `TEST_PYPI_API_TOKEN` and `PYPI_API_TOKEN` for manual publish jobs

## Promotion Flow

### Step 1: Publish to TestPyPI

Run workflow:
- `.github/workflows/publish-testpypi.yml`

Then verify in a fresh environment:

```bash
python -m venv /tmp/release-check-venv
source /tmp/release-check-venv/bin/activate
python -m pip install -U pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple py-crystal-seed==<version>
python -c "import py_crystal_seed; print(py_crystal_seed.__name__)"
```

The workflow uses a two-job boundary (`build-sign` then `verify-publish`), re-verifies signatures in the publish job, and fails if signature bundles are missing.

### Step 2: Publish to PyPI

Run workflow:
- `.github/workflows/publish-pypi.yml`

Trigger options:
- manual (`workflow_dispatch`)
- publish a GitHub release

GitLab equivalent:
- tag push triggers `release_build_sign` and `release_verify_gate`
- run `release_publish_testpypi` or `release_publish_pypi` manually after verify gate passes

### Step 3: Post-Release Verification

Verify install from PyPI:

```bash
python -m venv /tmp/release-prod-check-venv
source /tmp/release-prod-check-venv/bin/activate
python -m pip install -U pip
python -m pip install py-crystal-seed==<version>
python -c "import py_crystal_seed; print(py_crystal_seed.__name__)"
```

The workflow uses a two-job boundary (`build-sign` then `verify-publish`), re-verifies signatures in the publish job, and fails if signature bundles are missing.

## Rollback / Recovery

Python package versions are immutable on PyPI. If a bad release is published:

1. Do not attempt overwrite.
2. Yank the bad version on PyPI.
3. Prepare a fixed patch version.
4. Re-run the same promotion flow (TestPyPI -> PyPI).
5. Document incident and remediation in release notes.
