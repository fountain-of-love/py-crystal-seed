# Turn into a GitHub Template repository

### Goal

Make the repo reusable via **Use this template** and document the workflow.

### Code changes

None (template flag is UI setting).

### Documentation change

Add a section in `README.md`:

#### Suggested README section: “Using this as a template”

````markdown
## Using this as a template

This repository is intended to be used as a GitHub template.

### Option A: Use GitHub “Use this template”
1. Click **Use this template** on GitHub.
2. Create your new repository.
3. Clone it locally.

Then bootstrap:

```bash
make setup
make check
````

### Option B: Clone and rename manually

If you prefer copying the repository and renaming the package, see the **Renaming the project** section above.

```

### GitHub UI action (manual)
On GitHub:
- Repo → **Settings** → **Template repository** → enable it.

### Commit message
```

docs: document using this repository as a template

```