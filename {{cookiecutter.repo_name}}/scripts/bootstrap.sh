#!/usr/bin/env bash
set -e

VENV="venv"
PYTHON="python3.12"
FORCE_RECREATE="${FORCE_RECREATE:-0}"
SKIP_PIP_UPGRADE="${SKIP_PIP_UPGRADE:-0}"

if [ "$FORCE_RECREATE" = "1" ] && [ -d "$VENV" ]; then
  echo "Recreating virtual environment..."
  rm -rf "$VENV"
fi

if [ ! -d "$VENV" ]; then
  echo "Creating virtual environment..."
  $PYTHON -m venv "$VENV"
else
  echo "Reusing existing virtual environment..."
fi

if [ "$SKIP_PIP_UPGRADE" = "1" ]; then
  echo "Skipping build tooling upgrade (SKIP_PIP_UPGRADE=1)."
else
  echo "Upgrading build tooling..."
  if ! ./$VENV/bin/python -m pip install --upgrade pip setuptools wheel; then
    echo "Build tooling upgrade failed; continuing with existing toolchain."
  fi
fi

echo "Installing project (editable)..."
./$VENV/bin/python -m pip install -e .

if [ -d "./libs" ]; then
  echo "Installing local guardrail libraries (editable)..."
  ./$VENV/bin/python -m pip install --no-build-isolation \
    -e ./libs/guardrails-architecture \
    -e ./libs/guardrails-release \
    -e ./libs/guardrails-ops \
    -e ./libs/guardrails-governance
fi

echo "Installing dev dependencies..."
./$VENV/bin/python -m pip install -e '.[dev]'

echo ""
echo "Bootstrap complete."
echo "Activate with: source venv/bin/activate"
echo "Run tests with: pytest"
