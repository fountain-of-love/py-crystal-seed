VENV := venv
PY := $(VENV)/bin/python

.PHONY: setup check test hooks hooks-refresh clean help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'

setup: ## Create environment, install dev deps, install hooks
	@chmod +x scripts/bootstrap.sh || true
	@chmod +x scripts/test.sh || true
	@./scripts/bootstrap.sh
	@$(PY) -m pip install -e '.[dev]'
	@$(PY) -m pre_commit install

check: ## Run tests and pre-commit hooks
	@$(MAKE) hooks-refresh
	@./scripts/test.sh
	@$(PY) -m pre_commit run --all-files

test: ## Run tests only
	@./scripts/test.sh

hooks: ## Install pre-commit hooks
	@$(PY) -m pre_commit install

hooks-refresh: ## Clean and reinstall hooks
	@$(PY) -m pre_commit clean
	@$(PY) -m pre_commit uninstall || true
	@$(PY) -m pre_commit install

clean: ## Remove virtualenv and caches
	rm -rf $(VENV) .pytest_cache .mypy_cache __pycache__
