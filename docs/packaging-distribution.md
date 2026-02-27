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

## Why This Is Kept Separate

- Packaging/publishing is high impact and not needed for every feature PR.
- The default engineering path remains fast (`make check` + tests + static checks).
- Release operations are explicit, auditable, and opt-in.
