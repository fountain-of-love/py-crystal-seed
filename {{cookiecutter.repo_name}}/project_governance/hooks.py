"""Optional local governance hooks.

Central guardrails always run first from shared `guardrails-*` libraries.
If a hook is present, it runs after the central guard and may fail the command.
Use these hooks to add project-specific policy, not to weaken central policy.
Return `0`/`None` for pass, non-zero for failure.
"""

from __future__ import annotations

from pathlib import Path


def check_adr_quality(repo_root: Path) -> int | None:
    return 0


def check_docs_drift(repo_root: Path) -> int | None:
    return 0


def check_package_boundaries(repo_root: Path) -> int | None:
    return 0


def check_release_policy(repo_root: Path) -> int | None:
    return 0


def check_version_evolution(repo_root: Path, argv: list[str]) -> int | None:
    return 0


def check_waivers(repo_root: Path) -> int | None:
    return 0


def run_ops_gates(repo_root: Path, argv: list[str]) -> int | None:
    return 0
