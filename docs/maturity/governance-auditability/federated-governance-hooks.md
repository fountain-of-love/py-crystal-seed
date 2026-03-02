# Federated Governance Hooks

Purpose:
- keep central governance mandatory across all derived projects
- allow project-specific governance policy without forking central guardrail libraries
- make maturity upgrades flow primarily through dependency bumps, not copy-pasted scripts

## Model

This template uses a federated governance model:
1. central guardrail libraries run first
2. optional local project governance hooks run second
3. local hooks may add stricter policy, but they must not replace the central baseline

This gives two guarantees:
- every project gets the same centrally maintained minimum governance bar
- each project can add domain- or context-specific rules safely

## Execution Contract

The stable entrypoints remain the local wrapper scripts in `tools/`.
Each wrapper follows the same sequence:
1. load the central guardrail library (`guardrails-*`)
2. execute the central check
3. stop immediately on central failure
4. if central passes, try to import `project_governance.hooks`
5. run the matching local hook when present

This makes the local layer additive only.

## Local Hook Location

Derived projects can define local governance hooks in:
- `project_governance/hooks.py`

This module is optional.
If it is absent, only the central guardrail libraries run.

Starter functions are provided by the template as no-op hooks:
- `check_adr_quality(repo_root)`
- `check_docs_drift(repo_root)`
- `check_package_boundaries(repo_root)`
- `check_release_policy(repo_root)`
- `check_version_evolution(repo_root, argv)`
- `check_waivers(repo_root)`
- `run_ops_gates(repo_root, argv)`

Return contract:
- `0` or `None`: pass
- non-zero: fail the wrapper command

## Why This Exists

Without this hook model, teams typically choose one of two bad options:
- fork the central scripts and drift away from the baseline
- keep only central rules and lose project-specific policy enforcement

Federation avoids both:
- central rules stay upgradeable through library versions
- local rules stay close to the project that owns the context

## Upgrade Path

Generated projects should treat these as normal dependencies:
- `guardrails-governance`
- `guardrails-release`
- `guardrails-architecture`
- `guardrails-ops`

When those versions are bumped:
- central behavior tightens automatically
- local hooks remain intact as a narrow extension seam
- no command or CI interface changes should be required

## Design Rules

- Keep `tools/check_*.py` as thin wrappers only.
- Keep central governance in shared libraries.
- Keep local project policy inside `project_governance/hooks.py` or small local helper modules it calls.
- Do not weaken central checks from local hooks.
- Prefer config-driven local checks when possible.

## Example Use Cases

Examples of good local hook usage:
- extra package-boundary rules for a domain split not covered by the template default
- mandatory ADR categories for a regulated subsystem
- stricter waiver ownership rules for production-critical components
- additional observability assertions tied to a domain workflow

Examples of bad usage:
- skipping the central check when local policy disagrees
- mutating shared library behavior inside the project repo
- duplicating central guard logic into local hooks

## Operational Benefit

This model keeps the cookiecutter template lean while making governance distributable.
The template carries:
- stable wrappers
- config
- docs
- optional local hook stubs

The heavy governance logic evolves centrally in shared libraries.
That is the mechanism that allows generated projects to mature by dependency bump instead of governance-script copy/paste.
