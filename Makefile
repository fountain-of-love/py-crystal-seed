VENV := venv
PY := $(VENV)/bin/python

.PHONY: setup check test hooks hooks-refresh clean

# --- Core actions ---

help: ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

setup: ## Create/refresh environment and install dev tooling
	@chmod +x scripts/bootstrap.sh || true
	@chmod +x scripts/test.sh || true
	@chmod +x scripts/ensure-exec.sh 2>/dev/null || true
	@./scripts/bootstrap.sh
	@$(PY) -m pip install -e '.[dev]'
	@$(PY) -m pre_commit install

check: ## Run tests + pre-commit checks (with hook refresh to avoid stale caches)
	@$(MAKE) hooks-refresh
	@./scripts/test.sh
	@$(PY) -m pre_commit run --all-files

# --- Helpers ---

test: ## Run test suite via canonical script
	@./scripts/test.sh

hooks: ## Install pre-commit hooks
	@$(PY) -m pre_commit install

hooks-refresh: ## Clean and reinstall hooks (pre-commit caches hooks)
	@$(PY) -m pre_commit clean
	@$(PY) -m pre_commit uninstall || true
	@$(PY) -m pre_commit install

clean: ## Remove venv and caches
	rm -rf $(VENV) .pytest_cache .mypy_cache __pycache__
