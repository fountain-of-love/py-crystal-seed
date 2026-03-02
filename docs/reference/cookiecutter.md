# Project Templating: GitHub Templates & Cookiecutter

This repository is designed to be highly reusable. We provide two distinct paths for creating new projects: **GitHub Templates** for simplicity and **Cookiecutter** for automated, parameterized generation. This document explains the mechanics, the intent, and how to choose the right path for your needs.

---

## Quick Navigation

* [Cookiecutter Concept](#what-cookiecutter-is-conceptually)
* [GitHub Template Concept](#what-a-github-template-repository-is-conceptually)
* [Comparison at a Glance](#the-difference-in-one-sentence)
* [Why We Support Both](#why-use-both-in-the-same-project)
* [Workflow for Developers](#the-combined-workflow-for-developers)
* [Technical Interaction](#how-they-interact-technically)
* [Maturity Levels](#why-this-is-powerful-for-your-template)

---

## What Cookiecutter is (conceptually)

Cookiecutter is a **project generator**. It functions as a code "mold" that produces a unique project instance based on user input.



**The Mechanics:**
1.  **The Blueprint:** A folder containing template files with placeholders (e.g., `{{cookiecutter.repo_name}}`).
2.  **The Prompt:** A `cookiecutter.json` file that asks the user for variables (name, author, version).
3.  **The Output:** A brand new project directory where all names are substituted and the structure is customized to the answers provided.

**Example:**
* **Template:** `cookiecutter/{{cookiecutter.repo_name}}/src/{{cookiecutter.package_name}}/main.py`
* **User Input:** `repo_name = py-weather-core`
* **Result:** `py-weather-core/src/py_weather_core/main.py`

---

## What a GitHub Template repository is (conceptually)

A GitHub Template repository is a **structural copy**. It is essentially a "Copy this repository" button with a polished user interface.

**The Mechanics:**
* It copies the files exactly as they exist in the master branch.
* It does **no** transformation (no renaming, no variable substitution).
* It is perfect for quick starts where manual renaming of a few folders is acceptable.

---

## The Difference in One Sentence

| Tool | Action | Outcome |
| :--- | :--- | :--- |
| **GitHub Template** | Copies the repo exactly | A clone of the existing structure |
| **Cookiecutter** | Generates from a blueprint | A customized, parameterized project |

---

## Why use both in the same project?

They serve different audiences and different levels of maturity.

* **GitHub Templates** are for beginners, solo developers, or quick internal forks where extra tooling is undesirable.
* **Cookiecutter** is for teams and organizations with strong consistency requirements who need to onboard at scale with zero manual "find and replace" risk.

---

## The Combined Workflow for Developers

Contributors can choose their preferred "entry door" based on their needs:

### Option A: "I just want a quick start"
Use the **GitHub Template**:
1.  Click **"Use this template"** on the GitHub UI.
2.  Clone the new repository.
3.  Run `make setup` and `make check`.
4.  Manually rename the core package directory.

### Option B: "I want a properly named project from day one"
Use **Cookiecutter**:
1.  Clone this template repository.
2.  Ensure Cookiecutter is installed: `pip install cookiecutter`.
3.  Run the generator: `cookiecutter cookiecutter/`.
4.  Answer the prompts for repo name and package name.
5.  Enter the newly generated folder and run `make setup`.

---

## How they interact technically

The two systems are completely decoupled, which ensures architectural stability:
* The `/cookiecutter/` directory contains the **blueprint**.
* The `/src/` directory contains a **working example**.

When someone runs Cookiecutter, it reads from the `/cookiecutter/` folder and creates a new project elsewhere on the disk. It does **not** modify the template repository itself. This means the template remains a stable, testable project in its own right.



---

## Why this is powerful

By combining these tools, the project scales from hobby usage to enterprise-grade platform engineering:

| User Type | Recommended Path |
| :--- | :--- |
| **Explorer** | Browses the repo |
| **Solo Developer** | GitHub Template |
| **Team / Org** | Cookiecutter |
| **CI/CD Pipelines** | Cookiecutter + Scripts |

---

## The Big Picture

This is not just "adding tooling"—it is building a layered, professional system design:
1.  **Core Structure:** The physical files.
2.  **Deterministic Tooling:** The `Makefile` and `scripts/`.
3.  **Template Usage:** Easy manual starts via GitHub.
4.  **Generator Usage:** Scalable automation via Cookiecutter.

Each layer builds on the previous one, ensuring the workflow feels **architected** rather than just assembled.