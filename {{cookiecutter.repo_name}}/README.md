# {{cookiecutter.repo_name}}

{{cookiecutter.project_description}}

This project was generated using the **py-crystal-seed** template, a professional-grade Python project foundation focused on structural clarity, reproducibility, and long-term maintainability.

It includes best practices out of the box:
- `src/`-based package layout
- isolated virtual environment setup
- Makefile-based workflow (`make setup`, `make check`)
- pre-commit hooks for local quality gates
- Ruff linting and formatting checks
- Pyright static type checks
- Optional packaging/publishing pipeline (build, artifact checks, release workflows)
- pytest-based test suite
- CI-ready structure automatically via GitHub Actions on push/PR (see .github/workflows/tests.yml).

---

## Quick start

From the project root:

```bash
make setup
make check
````

This will:

* create a virtual environment
* install dependencies
* install pre-commit hooks
* run the test suite

You should now have a fully working development environment.

---

## Running the project

```bash
python -m {{cookiecutter.package_name}}.main
```

---

## Project structure

```
{{cookiecutter.repo_name}}/
├── src/{{cookiecutter.package_name}}/
├── tests/
├── scripts/
├── dev-ops/
├── pyproject.toml
├── Makefile
└── README.md
```

Key directories:

* `src/` → application code
* `tests/` → test suite
* `scripts/` → bootstrap and test helpers
* `dev-ops/` → development workflow documentation

---

## Development workflow

Common commands:

```bash
make setup   # bootstrap environment
make smoke   # run smoke matrix + import-boundary guardrail
make check   # run smoke matrix + pre-commit hooks
make test    # run tests only
make lint    # run Ruff checks
make format  # apply Ruff formatting/fixes
make typecheck # run Pyright checks
make package-build   # build wheel + sdist
make package-check   # validate dist metadata with twine
make package-install # install built wheel locally
make docs-drift      # enforce docs drift policy
make waivers-check   # validate waiver registry and expiry
make release-policy  # enforce SemVer/tag/changelog policy
make release-ready   # run full release readiness gate
make clean   # remove virtualenv and caches
```

For more details, see:

* `scripts/README.md`
* `dev-ops/README.md`
* `ENGINEERING_PRACTICES.md`
* `tools/README.md`
* `RELEASING.md`

---

## Origin

This project was generated from the **py-crystal-seed** template.

The template focuses on:

* explicit structure over implicit conventions
* reproducible environments
* tooling that scales from solo dev to teams
* early enforcement of quality gates

If you are maintaining this project long-term, you may want to keep that structure intact.

---

## License

Add your license information here.

```
```

This README:

- ✅ Is **short enough to be readable**
- ✅ Let's you explain what the project is  
- ✅ Credits the template (without overwhelming the project identity)  
- ✅ Mentions Makefile, pre-commit, CI, structure  
- ✅ Gives immediate actionable commands  
- ✅ Feels like a real project README, not template documentation  
- ✅ Scales from solo dev to professional team use  

Feels grounded. Not preachy. Still principled.
