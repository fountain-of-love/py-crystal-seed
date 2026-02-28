#!/usr/bin/env bash
set -euo pipefail

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

exec "$PY" ./tools/run_ops_gates.py "$@"
