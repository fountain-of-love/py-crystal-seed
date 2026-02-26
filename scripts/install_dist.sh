#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

if [ ! -x "$PY" ] || [ ! -x "$PIP" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

WHEEL="$(ls -1 dist/*.whl 2>/dev/null | head -n 1 || true)"
if [ -z "$WHEEL" ]; then
  echo "No wheel found under dist/."
  echo "Run ./scripts/build_dist.sh first."
  exit 1
fi

"$PIP" install --force-reinstall "$WHEEL"
echo "[package] Installed wheel: $WHEEL"
