VENV := venv
PY := $(VENV)/bin/python

.PHONY: setup check smoke test lint format typecheck hooks hooks-refresh clean help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'

setup: ## Create environment, install dev deps, install hooks
	@chmod +x scripts/bootstrap.sh || true
	@chmod +x scripts/test.sh || true
	@chmod +x scripts/lint.sh || true
	@chmod +x scripts/format.sh || true
	@chmod +x scripts/typecheck.sh || true
	@chmod +x tools/smoke_matrix.sh || true
	@./scripts/bootstrap.sh
	@$(PY) -m pip install -e '.[dev]'
	@$(PY) -m pre_commit install

check: ## Run smoke matrix + pre-commit hooks
	@$(MAKE) hooks-refresh
	@$(MAKE) smoke
	@$(PY) -m pre_commit run --all-files

test: ## Run tests only
	@./scripts/test.sh

smoke: ## Run smoke matrix (lint + typecheck + tests + import-boundary guard)
	@./tools/smoke_matrix.sh

lint: ## Run Ruff linting + formatting checks
	@./scripts/lint.sh

format: ## Apply Ruff auto-fixes and formatting
	@./scripts/format.sh

typecheck: ## Run Pyright static type checks
	@./scripts/typecheck.sh

hooks: ## Install pre-commit hooks
	@$(PY) -m pre_commit install

hooks-refresh: ## Clean and reinstall hooks
	@$(PY) -m pre_commit clean
	@$(PY) -m pre_commit uninstall || true
	@$(PY) -m pre_commit install

clean: ## Remove virtualenv and caches
	rm -rf $(VENV) .pytest_cache .ruff_cache .pyright __pycache__
