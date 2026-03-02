#!/usr/bin/env bash
set -e

echo "[smoke] Running lint"
./scripts/lint.sh

echo "[smoke] Running type checks"
./scripts/typecheck.sh

echo "[smoke] Running tests"
./scripts/test.sh

echo "[smoke] Running version evolution guardrail"
./venv/bin/python ./tools/check_version_import_boundaries.py

echo "[smoke] Running package boundary guardrail"
./venv/bin/python ./tools/check_package_boundaries.py

echo "[smoke] Running refactoring guardrail"
./venv/bin/python ./tools/check_refactoring_guard.py

echo "[smoke] Running ADR quality guardrail"
./venv/bin/python ./tools/check_adr_quality.py

echo "[smoke] Smoke matrix passed"
