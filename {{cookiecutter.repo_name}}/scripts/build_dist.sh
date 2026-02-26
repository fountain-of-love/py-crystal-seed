#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

rm -rf dist build *.egg-info src/*.egg-info
"$PY" -m build --no-isolation

echo "[package] Built distribution artifacts in ./dist"
