VENV := venv
PY := $(VENV)/bin/python

.PHONY: setup check smoke docs-drift waivers-check release-policy release-ready supplychain-scan sbom verify-signatures supplychain-check test lint format typecheck package-build package-check package-install package-publish-test package-publish hooks hooks-refresh clean help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'

setup: ## Create environment, install dev deps, install hooks
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
	@chmod +x scripts/security_scan.sh || true
	@chmod +x scripts/generate_sbom.sh || true
	@chmod +x scripts/verify_signatures.sh || true
	@chmod +x tools/smoke_matrix.sh || true
	@chmod +x tools/check_docs_drift.py || true
	@chmod +x tools/check_waivers.py || true
	@chmod +x tools/check_release_policy.py || true
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

docs-drift: ## Check required docs and change-aware docs drift policy
	@$(PY) ./tools/check_docs_drift.py

waivers-check: ## Validate waiver registry format and expiry rules
	@$(PY) ./tools/check_waivers.py

release-policy: ## Validate SemVer/tag policy and changelog coupling
	@$(PY) ./tools/check_release_policy.py

release-ready: ## Run release readiness gate (quality + package build/check)
	@$(MAKE) check
	@$(MAKE) waivers-check
	@$(MAKE) package-build
	@$(MAKE) package-check

supplychain-scan: ## Run dependency integrity/vulnerability scanning
	@./scripts/security_scan.sh

sbom: ## Generate CycloneDX SBOM artifact
	@./scripts/generate_sbom.sh

verify-signatures: ## Verify Sigstore bundles for built distributions
	@./scripts/verify_signatures.sh

supplychain-check: ## Run supply-chain checks (scan + sbom)
	@$(MAKE) supplychain-scan
	@$(MAKE) sbom

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

hooks-refresh: ## Clean and reinstall hooks
	@$(PY) -m pre_commit clean
	@$(PY) -m pre_commit uninstall || true
	@$(PY) -m pre_commit install

clean: ## Remove virtualenv and caches
	rm -rf $(VENV) .pytest_cache .ruff_cache .pyright dist build artifacts *.egg-info src/*.egg-info __pycache__
