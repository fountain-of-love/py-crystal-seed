#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"
OUT_DIR="artifacts/sbom"
OUT_FILE="$OUT_DIR/cyclonedx-sbom.json"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

mkdir -p "$OUT_DIR"
"$PY" -m cyclonedx_py environment --output-file "$OUT_FILE"

echo "[supply-chain] SBOM generated at $OUT_FILE"
