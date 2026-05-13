"""Governance guardrail package extracted from the template core."""

__all__ = [
    "GuardResult",
    "check_adr_quality",
    "check_coverage_governance",
    "check_docs_drift",
    "check_maturity_evidence",
    "check_waivers",
    "report_weekly",
    "run_adr_quality_check",
    "run_coverage_governance_check",
    "run_docs_drift_check",
    "run_maturity_evidence_check",
    "run_waiver_check",
]

from .adr_quality import check_adr_quality, run_adr_quality_check
from .coverage_governance import check_coverage_governance, run_coverage_governance_check
from .docs_drift import check_docs_drift, run_docs_drift_check
from .maturity_evidence import check_maturity_evidence, run_maturity_evidence_check
from .result import GuardResult
from .waivers import check_waivers, run_waiver_check
from .weekly_report import report_weekly
