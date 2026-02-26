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

if [ -z "${TEST_PYPI_API_TOKEN:-}" ]; then
  echo "Missing TEST_PYPI_API_TOKEN environment variable."
  exit 1
fi

TWINE_USERNAME="__token__" \
TWINE_PASSWORD="$TEST_PYPI_API_TOKEN" \
  "$PY" -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

echo "[package] Published artifacts to TestPyPI"
