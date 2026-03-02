#!/usr/bin/env bash
set -euo pipefail

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

./scripts/require_python_modules.sh "$PY" guardrails_ops

exec "$PY" ./tools/run_ops_gates.py "$@"
