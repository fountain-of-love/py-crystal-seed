#!/usr/bin/env bash
set -e

VENV="venv"
PYTHON="python3.12"

echo "Creating virtual environment..."
rm -rf "$VENV"
$PYTHON -m venv "$VENV"

echo "Upgrading build tooling..."
./$VENV/bin/python -m pip install --upgrade pip setuptools wheel

echo "Installing project (editable)..."
./$VENV/bin/python -m pip install -e .

if [ -d "./libs" ]; then
  echo "Installing local guardrail libraries (editable)..."
  for lib in \
    ./libs/guardrails-governance \
    ./libs/guardrails-release \
    ./libs/guardrails-architecture \
    ./libs/guardrails-ops; do
    if [ -f "$lib/pyproject.toml" ]; then
      ./$VENV/bin/python -m pip install -e "$lib"
    fi
  done
fi

echo "Installing dev dependencies..."
./$VENV/bin/python -m pip install -e '.[dev]'

echo ""
echo "Bootstrap complete."
echo "Activate with: source venv/bin/activate"
echo "Run tests with: pytest"
