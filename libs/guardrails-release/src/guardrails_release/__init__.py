"""Release guardrail package extracted from the template core."""

__all__ = ["GuardResult", "check_release_policy", "run_release_policy_check"]

from .release_policy import check_release_policy, run_release_policy_check
from .result import GuardResult
