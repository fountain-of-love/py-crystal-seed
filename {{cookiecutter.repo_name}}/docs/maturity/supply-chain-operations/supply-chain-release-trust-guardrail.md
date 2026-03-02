# Supply-Chain and Release Trust Guardrail

## Purpose

Prevent untrusted artifacts from reaching consumers by enforcing dependency and artifact trust controls.

## Enforcement

Local commands:
- `make supplychain-scan`
- `make sbom`
- `make supplychain-check`
- `make verify-signatures`

## Controls

1. Dependency integrity
- `pip check`

2. Vulnerability scanning
- `pip-audit`

3. SBOM generation
- CycloneDX SBOM at `artifacts/sbom/cyclonedx-sbom.json`

4. Artifact trust
- Sigstore signing + verification
- build provenance attestation for distribution artifacts

5. Verify-before-publish gates
- publish blocked if signature bundles are missing or verification fails

## CI Integration

GitHub:
- `supply-chain.yml`
- `package-validation.yml`
- `publish-testpypi.yml`
- `publish-pypi.yml`

GitLab:
- `.gitlab-ci.yml` release flow:
  - `release_build_sign`
  - `release_verify_gate`
  - manual publish jobs after verify gate

## Policy Intent

Security and trust checks are explicit release lanes, not hidden one-off steps.
