# CI pipeline (GitHub Actions)

## Goal
Automatically run the test suite on every push and pull request, across multiple Python versions.

This provides:
- fast feedback for contributors
- a reliable quality gate before merging
- prevention of regressions as the template evolves

## What changed
Added:

- `.github/workflows/tests.yml`

## How it works
GitHub Actions runs a matrix build:

- Python 3.10
- Python 3.11
- Python 3.12

For each version it:
1. checks out the repository
2. installs the project in editable mode with dev dependencies:
   - `python -m pip install -e '.[dev]'`
3. executes the test suite:
   - `python -m pytest -q`

## Why this design
### Why a Python matrix?
Templates should be forward compatible. A matrix ensures the template works for multiple supported versions and highlights version-specific issues early.

### Why editable install in CI?
Editable installs validate that:
- packaging metadata is correct
- `src/` layout is correctly configured
- imports behave like a real installed package (not “working directory magic”)

### Why `python -m pip` / `python -m pytest`?
This ensures the tooling is bound to the selected interpreter in the matrix and prevents PATH-related confusion.

## Verification
After pushing this commit:
- GitHub Actions should run automatically on push/PR.
- A passing run confirms both packaging and tests are healthy.

## Architectural placement
CI is a **Quality Gate** layer:
- local quality gate: pre-commit (commit-time)
- remote quality gate: CI (push/PR-time)

Together they prevent regressions from entering the template history.

## Packaging CI (separate lane)

Packaging is handled in dedicated workflows so it does not interfere with default development checks:

- `package-validation.yml`: build + twine check + wheel install smoke (push/PR)
- `package-install-matrix.yml`: cross-OS / cross-Python artifact install verification
- `publish-testpypi.yml`: publish to TestPyPI (manual)
- `publish-pypi.yml`: publish to PyPI (manual/release)
- both publish workflows enforce a two-job trust boundary (`build-sign` -> `verify-publish`) with Sigstore verification and fail on missing signature bundles
- `operations-gates.yml`: operational readiness lane (perf + leak + recovery + observability gates)

GitLab release-gate lane:
- `.gitlab-ci.yml`:
  - `ops_gates` (`quality` stage): operational readiness lane for merge requests/branches
  - `release_build_sign` (tag-only): build + twine check + Sigstore signing
  - `release_verify_gate` (tag-only): verifies signed artifacts from prior job before publish
  - `release_publish_testpypi` / `release_publish_pypi` (manual): blocked until verify gate passes

Governance workflows:
- `docs-drift.yml`: enforces docs update policy on PRs
- `release-policy.yml`: validates SemVer/tag/changelog policy
- `governance-waivers.yml`: validates waiver registry and expiry

Supply-chain workflows:
- `supply-chain.yml`: dependency integrity, vulnerability scan, CycloneDX SBOM artifact
- `package-validation.yml` additionally emits provenance attestations for `dist/*`
