#!/usr/bin/env bash
set -euo pipefail

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

if [ -z "${SIGSTORE_CERT_IDENTITY:-}" ]; then
  echo "Set SIGSTORE_CERT_IDENTITY to the expected workflow identity."
  echo "Example: https://github.com/<org>/<repo>/.github/workflows/publish-pypi.yml@refs/tags/v0.1.0"
  exit 1
fi

SIGSTORE_OIDC_ISSUER="${SIGSTORE_OIDC_ISSUER:-https://token.actions.githubusercontent.com}"

shopt -s nullglob
artifacts=(dist/*.whl dist/*.tar.gz)

if [ ${#artifacts[@]} -eq 0 ]; then
  echo "No distributions found in dist/. Run ./scripts/build_dist.sh first."
  exit 1
fi

for artifact in "${artifacts[@]}"; do
  bundle="${artifact}.sigstore.json"
  if [ ! -f "$bundle" ]; then
    echo "Missing Sigstore bundle for $artifact: $bundle"
    exit 1
  fi

  "$PY" -m sigstore verify identity "$artifact" \
    --bundle "$bundle" \
    --cert-identity "$SIGSTORE_CERT_IDENTITY" \
    --cert-oidc-issuer "$SIGSTORE_OIDC_ISSUER"
done

echo "[supply-chain] Sigstore verification passed for dist artifacts"
