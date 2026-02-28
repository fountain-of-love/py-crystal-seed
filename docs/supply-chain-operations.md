# Supply-Chain & Operations Hardening

## Goal

Raise confidence in dependency integrity and artifact trust without slowing default development loops.

## Local Commands

```bash
make supplychain-scan   # pip check + pip-audit
make sbom               # generate CycloneDX SBOM
make supplychain-check  # scan + sbom
make verify-signatures  # verify Sigstore bundles in dist/
make ops-gate           # run perf/leak/recovery/observability gates
make hardening-check    # run supply-chain + operations hardening lanes
```

`make supplychain-scan` upgrades the local packaging toolchain (`pip`, `wheel`) before vulnerability scanning, so advisories in outdated bootstrap tooling do not create false negatives/positives in normal project scans.

SBOM output:
- `artifacts/sbom/cyclonedx-sbom.json`

## CI Workflows

- `supply-chain.yml`
  - dependency integrity check (`pip check`)
  - vulnerability scan (`pip-audit`)
  - CycloneDX SBOM generation and artifact upload

- `package-validation.yml` (enhanced)
  - uploads distribution artifacts
  - emits build provenance attestation for `dist/*`
- `publish-testpypi.yml` and `publish-pypi.yml` (enhanced)
  - sign artifacts with Sigstore
  - verify signatures in an isolated downstream publish job
  - fail publish when required `.sigstore.json` bundles are missing
- `.gitlab-ci.yml` release lane
  - `release_build_sign` signs artifacts on tag pipelines
  - `release_verify_gate` verifies signatures before any publish job can run
  - manual publish jobs are blocked until verification passes

## Why This Is Separate

- Supply-chain checks can be slower or occasionally noisy due to upstream advisories.
- The default quality path remains deterministic (`make check`).
- Release/security posture still gets enforced in dedicated pipelines.

For detailed runtime-facing gate behavior, see:
- `docs/operations-hardening-gates.md`
