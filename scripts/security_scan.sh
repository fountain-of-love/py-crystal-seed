#!/usr/bin/env bash
set -euo pipefail

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

"$PY" -m pip check
"$PY" -m pip install -U pip wheel
"$PY" -m pip_audit

echo "[supply-chain] Dependency security scan passed"
