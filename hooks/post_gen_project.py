from __future__ import annotations

import os
import shutil
from pathlib import Path

# Files that should almost always be merged manually in existing repos.
# We refuse overwriting them by default to avoid stomping project-specific config.
DEFAULT_MANUAL_MERGE = {
    "pyproject.toml",
    "README.md",
    ".pre-commit-config.yaml",
    "pytest.ini",
    ".gitignore",
}


# Top-level paths we should never overwrite in "inject" mode (protect existing code).
# You can adjust this list to match your template philosophy.
PROTECTED_TOPLEVEL = {
    "src",
    "tests",
    "main.py",
    ".idea",
    ".git",
    "venv",
    ".venv",
}


def _csv_env_set(name: str) -> set[str]:
    """
    Parse a comma-separated env var into a set of stripped tokens.
    Example: CC_OVERWRITE="scripts,.github" -> {"scripts", ".github"}
    """
    raw = os.getenv(name, "").strip()
    if not raw:
        return set()
    return {token.strip() for token in raw.split(",") if token.strip()}


def _should_overwrite(dst: Path, overwrite_roots: set[str]) -> bool:
    """
    Decide whether an existing destination path may be overwritten.

    Rule: allow overwriting only when the destination is within one of the
    explicitly allowed top-level roots (e.g. ".github", "scripts").
    """
    # Determine the top-level folder/file name under repo root
    # Example dst = /repo/.github/workflows/ci.yml -> top = ".github"
    parts = dst.parts
    if not parts:
        return False

    # dst is an absolute-ish path; we only care about its name under target root.
    # We'll compute this relative later, so this function expects dst relative to target root.
    top = parts[0]
    return top in overwrite_roots


def _rm_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def move_all_children(
    src_dir: Path,
    dst_dir: Path,
    overwrite_roots: set[str],
    manual_merge: set[str],
    protected_toplevel: set[str],
) -> None:
    """
    Move all children from src_dir into dst_dir with explicit overwrite rules.

    - Never overwrite protected toplevel paths (src/tests/main.py/etc).
    - Never overwrite manual-merge files (pyproject.toml/etc) unless explicitly
      allowed via overwrite_roots.
    - Overwrite only within allowed roots (CC_OVERWRITE), and only when enabled
      (CC_INJECT already checked).
    """
    moved: list[str] = []
    overwritten: list[str] = []
    skipped: list[str] = []
    conflicts: list[str] = []

    for item in sorted(src_dir.iterdir(), key=lambda p: p.name):
        name = item.name
        dst = dst_dir / name

        # Protect certain top-level paths by default
        if name in protected_toplevel:
            skipped.append(f"{name} (protected)")
            continue

        # If destination doesn't exist, just move it.
        if not dst.exists():
            shutil.move(str(item), str(dst))
            moved.append(name)
            continue

        # Destination exists: decide overwrite policy
        # Always refuse overwriting manual-merge files unless explicitly allowed
        if name in manual_merge and name not in overwrite_roots:
            conflicts.append(f"{name} (manual merge)")
            continue

        # Allow overwrite only if the *top-level name itself* is in overwrite_roots
        # e.g. overwrite_roots={".github","scripts"} means those directories/files can be replaced.
        if name in overwrite_roots:
            _rm_path(dst)
            shutil.move(str(item), str(dst))
            overwritten.append(name)
            continue

        # Otherwise refuse (explicit is better than implicit)
        conflicts.append(f"{name} (exists, not in CC_OVERWRITE)")
        continue

    # Print summary in a developer-readable way
    print("[cookiecutter-inject] Summary")
    if moved:
        print("  Moved (new):")
        for x in moved:
            print(f"    - {x}")
    if overwritten:
        print("  Overwritten (explicit allowlist):")
        for x in overwritten:
            print(f"    - {x}")
    if skipped:
        print("  Skipped:")
        for x in skipped:
            print(f"    - {x}")
    if conflicts:
        print("  Conflicts (action required):")
        for x in conflicts:
            print(f"    - {x}")

        # Hard fail if there are conflicts, so developers are forced to resolve consciously
        raise SystemExit(
            "\n[cookiecutter-inject] Injection stopped due to conflicts.\n"
            "Resolve the listed items (merge/delete/rename) and re-run.\n"
            "Tip: set CC_OVERWRITE to explicitly allow overwriting certain top-level paths, e.g.\n"
            "  CC_INJECT=1 CC_OVERWRITE=.github,scripts cookiecutter . --output-dir <TARGET>\n"
        )


def main() -> None:
    # Explicit opt-in only (no auto-detection)
    if os.getenv("CC_INJECT") != "1":
        return

    generated_dir = Path.cwd()  # .../<project_name>
    target_dir = generated_dir.parent  # --output-dir you passed

    # Safety checks so it never injects into the wrong place
    if not (target_dir / ".git").exists():
        raise SystemExit(
            "[cookiecutter-inject] CC_INJECT=1 was set, but target is not a git repo "
            f"(missing {target_dir / '.git'}). Aborting."
        )

    # Overwrite allowlist, explicit (top-level only)
    overwrite_roots = _csv_env_set("CC_OVERWRITE")

    # Manual merge set can be extended/overridden via env var
    # Example: CC_MANUAL_MERGE="pyproject.toml,README.md" (replaces defaults if set)
    manual_merge = _csv_env_set("CC_MANUAL_MERGE") or set(DEFAULT_MANUAL_MERGE)

    # Protected toplevel can also be extended/overridden
    # Example: CC_PROTECT="src,tests,main.py"
    protected = _csv_env_set("CC_PROTECT") or set(PROTECTED_TOPLEVEL)

    print(f"[cookiecutter-inject] Injecting into existing repo: {target_dir}")
    overwrite_label = sorted(overwrite_roots) if overwrite_roots else "[]"
    print(f"[cookiecutter-inject] Overwrite allowlist (CC_OVERWRITE): {overwrite_label}")
    print(f"[cookiecutter-inject] Protected (CC_PROTECT): {sorted(protected)}")
    print(f"[cookiecutter-inject] Manual-merge (CC_MANUAL_MERGE): {sorted(manual_merge)}")

    move_all_children(
        src_dir=generated_dir,
        dst_dir=target_dir,
        overwrite_roots=overwrite_roots,
        manual_merge=manual_merge,
        protected_toplevel=protected,
    )

    # Remove now-empty generated folder
    try:
        generated_dir.rmdir()
    except OSError:
        shutil.rmtree(generated_dir)


if __name__ == "__main__":
    main()
