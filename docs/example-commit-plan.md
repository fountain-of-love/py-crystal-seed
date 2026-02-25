# Project Evolution: Step-by-Step Commit Plan

This document outlines the phased approach for maturing the repository from a basic structure to a professional template. Use the navigation below to jump to specific milestones.

---

## Quick Navigation

* [Commit 1: README & Rename](#commit-1-main-readme-refresh--rename-example)
* [Commit 2: Shell-Safe Install](#commit-2-make-zsh-safe-dev-install-instructions-everywhere)
* [Commit 3: CLI Entrypoint](#commit-3-add-proper-cli-entrypoint-so-it-runs-as-a-command)
* [Commit 4: Metadata & Badges](#commit-4-add-badges-and-minimal-project-metadata-polish)
* [Commit 5: Pre-commit Setup](#commit-5-add-pre-commit-configuration)
* [Commit 6: CI Pipeline](#commit-6-add-ci-pipeline-github-actions)
* [Commit 7: Template Readiness](#commit-7-turn-into-a-github-template-repository)
* [Commit 8: Cookiecutter Integration](#commit-8-cookiecutter-optional-but-powerful)

---

## Detail of Epics

### Commit 1: Main README refresh + rename example
**Goal:** Add the improved `README.md`, reference `dev-ops/README.md`, and update the rename example to `py-structural-anchor`.

**Changes:**
* `README.md`: Update content, add “how it differs” section, and update rename examples.
* **Optional:** Update starter output string in `src/py_crystal_seed/main.py` to match README (“The structure holds.”) and update `tests/test_main.py` accordingly.

**Result:** Documentation is aligned with the code; tests remain passing.

---

### Commit 2: Make zsh-safe dev install instructions everywhere
**Goal:** Eliminate the `.[dev]` shell glob "footgun" by adding quotes.

**Changes:**
* `dev-ops/README.md`: Replace `pip install -e .[dev]` with `pip install -e '.[dev]'`.
* Audit all other documentation files for unquoted extras.

**Result:** Instructions are copy-paste safe for Zsh, Bash, and CI environments.

---

### Commit 3: Add proper CLI entrypoint (so it runs as a command)
**Goal:** Enable users to run the package as a standalone command rather than `python -m ...`.

**Changes:**
* `pyproject.toml`: Add the script configuration:
  ```toml
  [project.scripts]
  py-crystal-seed = "py_crystal_seed.main:main"
  ```

* Ensure `main()` function exists in `main.py` and is stable.

**Result:** After installation, running `py-crystal-seed` works directly in the terminal.

---

### Commit 4: Add badges and minimal project metadata polish

**Goal:** Increase professional presentation with visual status indicators and legal clarity.

**Changes:**

* `README.md`: Add Shields.io badges (Build Status, Python Version, License).
* `LICENSE`: Add MIT or preferred license file.
* `CHANGELOG.md`: Initialize the version history.

**Result:** The project looks "production-ready" to external contributors.

---

### Commit 5: Add pre-commit configuration

**Goal:** Ensure formatting, linting, and basic tests run automatically before every commit.

**Changes:**

* `.pre-commit-config.yaml`: Define hooks for Ruff (lint/format) and Pyright.
* `dev-ops/README.md`: Add instructions for running `pre-commit install`.

**Result:** A local quality gate prevents "messy" commits from reaching the remote.

---

### Commit 6: Add CI pipeline (GitHub Actions)

**Goal:** Automate testing across multiple Python versions on every Push or PR.

**Changes:**

* `.github/workflows/tests.yml`: Configure the action to use `pip install -e '.[dev]'` and run `pytest`.

**Result:** Automated validation provides confidence for merging new code.

---

### Commit 7: Turn into a GitHub “Template repository”

**Goal:** Enable the “Use this template” button and document the bootstrapping process.

**Changes:**

* `README.md`: Add a "Using this as a template" section.
* **Manual Step:** Enable the "Template repository" checkbox in GitHub repository settings.

**Result:** The repository is now a reusable foundation for new projects.

---

### Commit 8: Cookiecutter (optional, but powerful)

**Goal:** Allow users to generate new projects using dynamic variables (Project Name, Author, etc.).

**Changes:**

* Add `cookiecutter/` template folder.
* Add `cookiecutter.json` with configuration variables.
* Update documentation to include Cookiecutter usage instructions.

**Result:** A single command generates a fully customized version of this repository structure.

```

Would you like me to adjust any of the anchor links or add specific technical details to the "Changes" sections?

```
