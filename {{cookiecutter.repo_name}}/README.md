# {{cookiecutter.repo_name}}

{{cookiecutter.project_description}}

This project was generated from the **py-crystal-seed** template.

## Included Engineering Defaults

- `src/`-based package layout
- isolated virtual environment workflow (`make setup`)
- Ruff linting + formatting checks
- Pyright static type checks
- pytest test suite
- smoke matrix orchestration
- version evolution guardrail
- package boundary guardrail (config-driven)
- ADR quality guardrail
- release policy, docs drift, and waiver governance checks
- packaging and publishing pipeline (build/check/install/publish)
- supply-chain and operations hardening gates

## Quick Start

```bash
make setup
make check
```

Run the package:

```bash
python -m {{cookiecutter.package_name}}.main
```

## Common Commands

```bash
make smoke
make check
make lint
make format
make typecheck
make test
make governance-check
make release-ready
make supplychain-check
make ops-gate
```

Governance-specific commands:

```bash
make package-boundaries-check
make adr-check
make docs-drift
make waivers-check
make release-policy
```

## Structure

```text
{{cookiecutter.repo_name}}/
├── src/{{cookiecutter.package_name}}/
├── tests/
├── tools/
├── scripts/
├── dev-ops/
├── docs/
├── pyproject.toml
└── Makefile
```

## Guardrail Externalization (Lean Template Strategy)

This repository keeps stable local guardrail entrypoints (`tools/check_*.py`, `make` targets).
As governance internals mature, move policy engines into shared versioned libraries and keep these local entrypoints as thin adapters.
Projects may add local governance in `project_governance/hooks.py`; those hooks run only after the central shared guardrail passes.

Result:
- generated projects stay lean
- maturity controls evolve centrally
- adoption is mainly dependency version bumping

## Documentation

- `dev-ops/README.md`
- `scripts/README.md`
- `tools/README.md`
- `docs/README.md`
- `docs/adr/ADR-0000-template.md`
- `DEVELOPER_README.md`
- `RELEASING.md`

## License

See `LICENSE`.
