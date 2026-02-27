# Supply-Chain & Operations Hardening

## Goal

Raise confidence in dependency integrity and artifact trust without slowing default development loops.

## Local Commands

```bash
make supplychain-scan   # pip check + pip-audit
make sbom               # generate CycloneDX SBOM
make supplychain-check  # scan + sbom
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

## Why This Is Separate

- Supply-chain checks can be slower or occasionally noisy due to upstream advisories.
- The default quality path remains deterministic (`make check`).
- Release/security posture still gets enforced in dedicated pipelines.
