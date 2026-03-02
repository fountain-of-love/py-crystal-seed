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
- Adapters call shared library APIs/CLIs once available.
- Repo-specific policy remains in local config files (`waivers.yml`, boundary configs, etc.).
- Project-specific extensions live in `project_governance/hooks.py` and run only after the central library check passes.

## Migration Phases

1. Implemented now: local scripts are thin adapters with stable command names.
2. Implemented now: policy logic is carved into reusable in-repo modules under `src/*/guardrails`.
3. Started now: the governance set is split into a separate package boundary at `src/guardrails_governance/`.
4. Started now: the release set is split into a separate package boundary at `src/guardrails_release/`.
5. Started now: the architecture set is split into a separate package boundary at `src/guardrails_architecture/`.
6. Started now: the operations set is split into a separate package boundary at `src/guardrails_ops/`.
7. Implemented now: these sets are consumed as external-style dependencies (`guardrails-*`) and kept as local dev copies under `libs/*` in this seed repo.
8. Next: publish/version these libraries independently and consume released versions in generated projects.
9. Later: keep adapters stable while switching backend implementation to released external libs only.
10. Implemented now: local projects can federate extra policy through additive `project_governance` hooks.
11. Ongoing: projects adopt improvements through library version upgrades.

## Non-goals

- no forced network/runtime dependency for local development
- no breaking changes to existing `make` and CI command surfaces

## Expected Outcome

- leaner generated projects
- centralized governance evolution
- lower adoption friction for Java-analog maturity controls across many repositories

## Template Decluttering Rule

Keep the cookiecutter template focused on:
- thin `tools/` adapters
- local policy/config files
- contributor-facing documentation

Do not keep growing duplicated policy engines inside the template copy.
New guard behavior should land in reusable modules first, then later in shared libraries.
