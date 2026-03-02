#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

./scripts/require_python_modules.sh "$PY" ruff

"$PY" -m ruff check --fix src tests scripts tools
"$PY" -m ruff format src tests scripts tools
