#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

if [ ! -d "dist" ]; then
  echo "No dist/ directory found."
  echo "Run ./scripts/build_dist.sh first."
  exit 1
fi

"$PY" -m twine check dist/*
echo "[package] Twine validation passed"
