# Quality Gate Architecture: Automated Testing & Pre-commit

This document outlines the implementation of a "Single Source of Truth" for project health. By centralizing test execution, we eliminate fragmentation and ensure consistent results across developer environments and CI.

---

## Quick Navigation

* [Core Concept: Automated Health](#the-goal-of-this-step-conceptually)
* [Step 1: Canonical Test Command](#step-1-establish-a-canonical-test-command)
* [Step 2: Pre-commit Integration](#step-2-wire-pre-commit-to-call-the-script-not-pytest-directly)
* [Step 3: Script Documentation](#step-3-update-scriptsreadmemd)
* [Step 4: Workflow & Intent](#step-4-update-dev-opsreadmemd-conceptual-layer)
* [Step 5: Dependency Management](#step-5-update-pyprojecttoml)
* [Final Architecture Overview](#final-architecture-after-this-commit)

---

## The Goal of This Step (Conceptually)

The objective is to ensure that when someone commits code, the project automatically checks its own health. This requires:

1.  **A canonical way** to run tests.
2.  **A hook** that calls that canonical command.
3.  **Documentation** that explains the system.
4.  **No duplicated logic** scattered across files.

---

## Step 1: Establish a canonical test command

We are moving away from multiple ways of running tests (PyCharm, manual pytest, etc.) to exactly one official entry point: `./scripts/test.sh`.

### Implementation
Create `scripts/test.sh` with the following content:

```bash
#!/usr/bin/env bash
set -e

VENV="venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Virtualenv not found at $VENV/"
  echo "Run ./scripts/bootstrap.sh first."
  exit 1
fi

exec "$PY" -m pytest -q