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

if [ -z "${PYPI_API_TOKEN:-}" ]; then
  echo "Missing PYPI_API_TOKEN environment variable."
  exit 1
fi

TWINE_USERNAME="__token__" \
TWINE_PASSWORD="$PYPI_API_TOKEN" \
  "$PY" -m twine upload dist/*

echo "[package] Published artifacts to PyPI"
