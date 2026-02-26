VENV := venv
PY := $(VENV)/bin/python
CC := $(VENV)/bin/cookiecutter

.PHONY: help setup check smoke docs-drift release-policy release-ready test lint format typecheck package-build package-check package-install package-publish-test package-publish hooks hooks-refresh clean new inject apply-safe

# --- Core actions ---

help: ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

setup: ## Create/refresh environment and install dev tooling
	@chmod +x scripts/bootstrap.sh || true
	@chmod +x scripts/test.sh || true
	@chmod +x scripts/lint.sh || true
	@chmod +x scripts/format.sh || true
	@chmod +x scripts/typecheck.sh || true
	@chmod +x scripts/build_dist.sh || true
	@chmod +x scripts/check_dist.sh || true
	@chmod +x scripts/install_dist.sh || true
	@chmod +x scripts/publish_testpypi.sh || true
	@chmod +x scripts/publish_pypi.sh || true
	@chmod +x tools/smoke_matrix.sh || true
	@chmod +x tools/check_docs_drift.py || true
	@chmod +x tools/check_release_policy.py || true
	@chmod +x scripts/ensure-exec.sh 2>/dev/null || true
	@./scripts/bootstrap.sh
	@$(PY) -m pip install -e '.[dev]'
	@$(PY) -m pre_commit install

check: ## Run smoke matrix + pre-commit checks
	@$(MAKE) hooks-refresh
	@$(MAKE) smoke
	@$(PY) -m pre_commit run --all-files

# --- Cookiecutter actions ---

apply-safe: ## Generate into TARGET folder without overwriting (safe mode)
	@if [ -z "$(TARGET)" ]; then \
		echo "Usage: make apply-safe TARGET=../captain-do"; \
		exit 1; \
	fi
	@$(CC) . --output-dir "$(TARGET)" --overwrite-if-exists=false

new: ## Greenfield: generate a new project folder inside OUT
	@if [ -z "$(OUT)" ]; then \
		echo "Usage: make new OUT=/path/to/parent/dir"; \
		exit 1; \
	fi
	@$(CC) . --output-dir "$(OUT)"

inject: ## Existing repo: inject into TARGET (explicit; requires CC_INJECT hook support)
	@if [ -z "$(TARGET)" ]; then \
		echo "Usage: make inject TARGET=/path/to/existing/repo"; \
		exit 1; \
	fi
	@CC_INJECT=1 $(CC) . --output-dir "$(TARGET)"

# --- Helpers ---

test: ## Run test suite via canonical script
	@./scripts/test.sh

smoke: ## Run smoke matrix (lint + typecheck + tests + import-boundary guard)
	@./tools/smoke_matrix.sh

docs-drift: ## Check required docs and change-aware docs drift policy
	@$(PY) ./tools/check_docs_drift.py

release-policy: ## Validate SemVer/tag policy and changelog coupling
	@$(PY) ./tools/check_release_policy.py

release-ready: ## Run release readiness gate (quality + package build/check)
	@$(MAKE) check
	@$(MAKE) package-build
	@$(MAKE) package-check

lint: ## Run Ruff linting + formatting checks
	@./scripts/lint.sh

format: ## Apply Ruff auto-fixes and formatting
	@./scripts/format.sh

typecheck: ## Run Pyright static type checks
	@./scripts/typecheck.sh

package-build: ## Build wheel + sdist in dist/
	@./scripts/build_dist.sh

package-check: ## Validate built distributions with twine
	@./scripts/check_dist.sh

package-install: ## Install built wheel into local venv
	@./scripts/install_dist.sh

package-publish-test: ## Publish dist artifacts to TestPyPI (needs TEST_PYPI_API_TOKEN)
	@./scripts/publish_testpypi.sh

package-publish: ## Publish dist artifacts to PyPI (needs PYPI_API_TOKEN)
	@./scripts/publish_pypi.sh

hooks: ## Install pre-commit hooks
	@$(PY) -m pre_commit install

hooks-refresh: ## Clean and reinstall hooks (pre-commit caches hooks)
	@$(PY) -m pre_commit clean
	@$(PY) -m pre_commit uninstall || true
	@$(PY) -m pre_commit install

clean: ## Remove venv and caches
	rm -rf $(VENV) .pytest_cache .ruff_cache .pyright dist build *.egg-info src/*.egg-info __pycache__/
