#!/usr/bin/env bash
set -e

echo "[smoke] Running lint"
./scripts/lint.sh

echo "[smoke] Running type checks"
./scripts/typecheck.sh

echo "[smoke] Running tests"
./scripts/test.sh

echo "[smoke] Running version import-boundary guardrail"
./venv/bin/python ./tools/check_version_import_boundaries.py

echo "[smoke] Smoke matrix passed"
