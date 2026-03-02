"""Architecture guardrail package extracted from the template core."""

__all__ = [
    "GuardResult",
    "check_package_boundaries",
    "check_refactoring_guard",
    "check_version_evolution",
    "run_package_boundary_check",
    "run_refactoring_guard_check",
    "run_version_evolution_check",
]

from .package_boundaries import check_package_boundaries, run_package_boundary_check
from .refactoring_guard import check_refactoring_guard, run_refactoring_guard_check
from .result import GuardResult
from .version_evolution import check_version_evolution, run_version_evolution_check
