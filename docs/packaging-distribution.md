# Packaging & Distribution Pipeline

## Goal

Provide a publish-ready, optional pipeline for building and distributing Python packages
without interfering with day-to-day development workflows.

This lane is intentionally separate from the default quality lane (`make check`).

## Local Packaging Commands

From project root:

```bash
make package-build        # build wheel + sdist
make package-check        # twine metadata validation
make package-install      # install wheel from dist/ into venv
```

Optional publish commands:

```bash
make package-publish-test # publish to TestPyPI (needs TEST_PYPI_API_TOKEN)
make package-publish      # publish to PyPI (needs PYPI_API_TOKEN)
```

For release operation steps and rollback guidance, see:
- `RELEASING.md`

Additional governance commands:

```bash
make docs-drift
make waivers-check
make release-policy
make release-ready
```

Supply-chain commands:

```bash
make supplychain-scan
make sbom
make supplychain-check
make verify-signatures # verify Sigstore bundles in dist/
```

## Pipeline Structure

### 1) Validation workflow

File:
- `.github/workflows/package-validation.yml`

Runs on push/PR:
1. install dev dependencies
2. build distributions (`python -m build`)
3. validate artifacts (`python -m twine check dist/*`)
4. install the built wheel
5. perform an import smoke check

This proves the package is buildable and consumable as an artifact, not only via editable install.

### 2) TestPyPI publish workflow

File:
- `.github/workflows/publish-testpypi.yml`

Trigger:
- manual (`workflow_dispatch`)

Secret required:
- none when using Trusted Publishing (OIDC)

### 3) PyPI publish workflow

File:
- `.github/workflows/publish-pypi.yml`

Triggers:
- manual (`workflow_dispatch`)
- GitHub release published

Secret required:
- none when using Trusted Publishing (OIDC)

Recommended:
- protect the `pypi` environment in GitHub with required reviewers
- publish to TestPyPI first, then promote to PyPI
- keep local token-based publish scripts for emergency/manual fallback only

### 4) GitLab release gate pipeline

File:
- `.gitlab-ci.yml`

Tag release flow:
1. `release_build_sign` builds distributions and signs with Sigstore (keyless via GitLab OIDC token).
2. `release_verify_gate` downloads prior artifacts and verifies signatures before any publish.
3. `release_publish_testpypi` / `release_publish_pypi` are manual and depend on verify gate success.

## Release trust controls

Both publish workflows now enforce:
1. release-policy validation (`tools/check_release_policy.py`)
2. `build-sign` job creates and signs `dist/*.whl` and `dist/*.tar.gz`
3. `verify-publish` job downloads those artifacts and re-verifies signatures in an isolated job boundary
4. hard failure if any distribution is missing a `.sigstore.json` bundle

Local verification command:

```bash
SIGSTORE_CERT_IDENTITY="https://github.com/<org>/<repo>/.github/workflows/publish-pypi.yml@refs/tags/vX.Y.Z" make verify-signatures
```

GitLab CI/CD variables needed for gated publish:
- `SIGSTORE_CERT_IDENTITY` (expected signing identity for verify gate)
- optional `SIGSTORE_OIDC_ISSUER` (defaults to `https://gitlab.com`)
- `TEST_PYPI_API_TOKEN` for TestPyPI publish job
- `PYPI_API_TOKEN` for PyPI publish job

## Why This Is Kept Separate

- Packaging/publishing is high impact and not needed for every feature PR.
- The default engineering path remains fast (`make check` + tests + static checks).
- Release operations are explicit, auditable, and opt-in.
