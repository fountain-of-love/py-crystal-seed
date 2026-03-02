# Guardrail Library Externalization

Purpose:
- keep this template lean
- avoid duplicating governance internals across generated projects
- distribute maturity upgrades through versioned guardrail libraries

## Problem

This template now carries strong governance controls (version evolution, docs drift, release policy, waivers, ADR quality, package boundaries).
If copied as raw scripts into every project, policy logic drifts and upgrade cost grows.

## Strategy

Use a two-layer model:
1. Stable local command facades in each repo (`make` targets and `tools/*.py` entrypoints).
2. Versioned shared guardrail libraries that implement policy internals.

The local facade remains stable while the backend implementation can evolve via dependency bumps.

## Target Architecture

- `tools/check_*.py` becomes thin adapters.
- Adapters call shared library APIs/CLIs.
- Repo-specific policy remains in local config files (`waivers.yml`, boundary configs, etc.).
- Project-specific extensions live in `project_governance/hooks.py` and run only after the central library check passes.
- Shared libraries are published as Python packages with stable CLI entrypoints and packaged resources.

## Migration Phases

1. Implemented now: local scripts are thin adapters with stable command names.
2. Implemented earlier: policy logic was first carved into reusable in-repo modules under `src/*/guardrails`.
3. Implemented now: governance, release, architecture, and ops are split into shared package boundaries under `libs/*`.
4. Implemented now: these sets are consumed as external-style dependencies (`guardrails-*`) in this seed repo.
5. Next: publish/version these libraries independently and consume released versions in generated projects.
6. Later: keep adapters stable while switching backend implementation to released external libs only.
7. Implemented now: local projects can federate extra policy through additive `project_governance` hooks.
8. Ongoing: projects adopt improvements through library version upgrades.

## Non-goals

- no forced network/runtime dependency for local development
- no breaking changes to existing `make` and CI command surfaces

## Expected Outcome

- leaner generated projects
- centralized governance evolution
- lower adoption friction for Java-analog maturity controls across many repositories

## Canonical Public Surface

The public contract should converge on:
- Python package dependency
- Python API for embedding and tests
- CLI entrypoints for pre-commit and CI
- repo-local manifests for project policy
- additive local hooks for project-specific tightening

See also:
- `guardrail-packaging-model.md`
- `guardrail-manifest-contract.md`
- `downstream-guardrail-consumption.md`

## Template Decluttering Rule

Keep the cookiecutter template focused on:
- thin `tools/` adapters
- local policy/config files
- contributor-facing documentation

Do not keep growing duplicated policy engines inside the template copy.
New guard behavior should land in reusable modules first, then later in shared libraries.
