#!/usr/bin/env bash
set -euo pipefail

VENV="${VENV:-venv}"
PY="$VENV/bin/python"
SYSTEM_PY="${SYSTEM_PY:-python3}"
OFFLINE_PYTHONPATH="src:libs/guardrails-governance/src:libs/guardrails-architecture/src:libs/guardrails-release/src:libs/guardrails-ops/src"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/."
  if ! command -v "$SYSTEM_PY" >/dev/null 2>&1; then
    echo "Run ./scripts/bootstrap.sh first."
    exit 1
  fi
fi

missing_modules=()
for module in pre_commit ruff pyright pytest yaml; do
  if ! "$PY" -c "import ${module}" >/dev/null 2>&1; then
    missing_modules+=("$module")
  fi
done

if [ "${#missing_modules[@]}" -eq 0 ]; then
  exec "$PY" -m pre_commit run --all-files
fi

echo "Commit gate dependencies are missing from $VENV:"
for module in "${missing_modules[@]}"; do
  echo "  - $module"
done
echo ""
echo "This repository now enforces a full-governance commit gate."
echo "Falling back to the offline validation lane for this commit:"
echo "  PYTHONPATH=\"$OFFLINE_PYTHONPATH\" $SYSTEM_PY -m pytest -q"
echo ""
PYTHONPATH="$OFFLINE_PYTHONPATH" "$SYSTEM_PY" -m pytest -q
echo ""
echo "Offline commit gate passed."
echo "Restore the full environment when a dependency source is available:"
echo "  SKIP_PIP_UPGRADE=1 ./scripts/bootstrap.sh"
echo "  $PY -m pip install -e '.[dev]'"
