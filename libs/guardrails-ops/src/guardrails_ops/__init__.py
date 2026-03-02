"""Operations guardrail package extracted from the template core."""

__all__ = ["GuardResult", "check_ops_gates", "run_ops_gates"]

from .ops import check_ops_gates, run_ops_gates
from .result import GuardResult
