
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

## `test.sh`

Runs the project test suite using the project’s virtual environment.

This script is used by:
- developers (manual testing)
- pre-commit hooks (commit-time validation)
- future CI pipelines

It enforces a single, canonical way of running tests.

### Usage

```bash
./scripts/test.sh
```

---

## `lint.sh`

Runs Ruff linting and formatting checks in validation mode.

### Usage

```bash
./scripts/lint.sh
```

---

## `format.sh`

Applies Ruff autofixes and formatting.

### Usage

```bash
./scripts/format.sh
```

---

## `typecheck.sh`

Runs static type checks with Pyright.

### Usage

```bash
./scripts/typecheck.sh
```

---

## `build_dist.sh`

Builds wheel and source distributions into `dist/`.

### Usage

```bash
./scripts/build_dist.sh
```

---

## `check_dist.sh`

Validates built distributions using Twine metadata checks.

### Usage

```bash
./scripts/check_dist.sh
```

---

## `install_dist.sh`

Installs the built wheel from `dist/` into the local virtual environment.

### Usage

```bash
./scripts/install_dist.sh
```

---

## `publish_testpypi.sh`

Publishes current `dist/` artifacts to TestPyPI.

Requires:
- `TEST_PYPI_API_TOKEN`

### Usage

```bash
./scripts/publish_testpypi.sh
```

---

## `publish_pypi.sh`

Publishes current `dist/` artifacts to PyPI.

Requires:
- `PYPI_API_TOKEN`

### Usage

```bash
./scripts/publish_pypi.sh
```

---

## `security_scan.sh`

Runs dependency integrity and vulnerability checks.
It upgrades `pip` and `wheel` in the local virtual environment before running `pip-audit`.

### Usage

```bash
./scripts/security_scan.sh
```

---

## `generate_sbom.sh`

Generates a CycloneDX SBOM at `artifacts/sbom/cyclonedx-sbom.json`.

### Usage

```bash
./scripts/generate_sbom.sh
```

---

## `verify_signatures.sh`

Verifies Sigstore bundles for distributions in `dist/`.

Requires:
- `SIGSTORE_CERT_IDENTITY`
- optional `SIGSTORE_OIDC_ISSUER` (defaults to `https://token.actions.githubusercontent.com`)

### Usage

```bash
SIGSTORE_CERT_IDENTITY="https://github.com/<org>/<repo>/.github/workflows/publish-pypi.yml@refs/tags/v0.1.0" ./scripts/verify_signatures.sh
```

---

## Philosophy

These scripts are not meant to hide complexity.
They exist to **encode the correct order of operations** so contributors do not have to remember it.

They act as executable documentation for how the project is meant to be used.

For smoke orchestration and architecture guardrails, see:
- `tools/README.md`
