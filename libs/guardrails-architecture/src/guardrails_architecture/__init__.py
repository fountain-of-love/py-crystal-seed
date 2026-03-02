"""Architecture guardrail package extracted from the template core."""

__all__ = ["run_package_boundary_check", "run_version_evolution_check"]

from .package_boundaries import run_package_boundary_check
from .version_evolution import run_version_evolution_check
