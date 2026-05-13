from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adr_quality import check_adr_quality as _engine_check_adr_quality
from .adr_quality import format_adr_quality_result
from .coverage_governance import check_coverage_governance as _engine_check_coverage_governance
from .coverage_governance import format_coverage_governance_result
from .docs_drift import check_docs_drift as _engine_check_docs_drift
from .docs_drift import format_docs_drift_result
from .maturity_evidence import check_maturity_evidence as _engine_check_maturity_evidence
from .maturity_evidence import format_maturity_evidence_result
from .result import GuardResult
from .waivers import check_waivers as _engine_check_waivers
from .waivers import format_waiver_result
from .weekly_report import report_weekly


def _repo_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    return parser


def _emit(result: GuardResult, *, output: str, formatter) -> int:
    if output == "json":
        print(result.to_json())
    else:
        print(formatter(result))
    return result.exit_code()


def check_adr(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate ADR quality.")
    parser.add_argument("--adr-dir", default="docs/adr")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    adr_dir = Path(args.adr_dir)
    if not adr_dir.is_absolute():
        adr_dir = (repo_root / adr_dir).resolve()
    result = _engine_check_adr_quality(adr_dir=adr_dir)
    return _emit(result, output=args.output, formatter=format_adr_quality_result)


def check_docs_drift_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate docs drift policy.")
    parser.add_argument("--diff-base", default="")
    parser.add_argument("--diff-head", default="HEAD")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    result = _engine_check_docs_drift(repo_root=repo_root, diff_base=args.diff_base, diff_head=args.diff_head)
    return _emit(result, output=args.output, formatter=format_docs_drift_result)


def check_waivers_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate waiver policy.")
    parser.add_argument("--config", default="waivers/waivers.yml")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    result = _engine_check_waivers(waiver_file=config)
    return _emit(result, output=args.output, formatter=format_waiver_result)


def check_coverage_governance_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate coverage governance policy.")
    parser.add_argument("--config", default="tools/coverage_governance.yml")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    result = _engine_check_coverage_governance(repo_root=repo_root, config_path=config)
    return _emit(result, output=args.output, formatter=format_coverage_governance_result)


def check_maturity_evidence_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Validate maturity evidence policy.")
    parser.add_argument("--config", default="tools/maturity_evidence.yml")
    parser.add_argument("--diff-base", default="")
    parser.add_argument("--diff-head", default="HEAD")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    result = _engine_check_maturity_evidence(
        repo_root=repo_root,
        config_path=config,
        diff_base=args.diff_base,
        diff_head=args.diff_head,
    )
    return _emit(result, output=args.output, formatter=format_maturity_evidence_result)


def report_weekly_cli(argv: list[str] | None = None) -> int:
    parser = _repo_parser("Generate weekly governance report.")
    parser.add_argument("--config", default="tools/weekly_reporting.yml")
    parser.add_argument("--history-dir", default="")
    parser.add_argument("--output-dir", default="artifacts/governance")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (repo_root / output_dir).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = (repo_root / config).resolve()
    history_dir = Path(args.history_dir) if args.history_dir else None
    if history_dir is not None and not history_dir.is_absolute():
        history_dir = (repo_root / history_dir).resolve()
    result = report_weekly(repo_root=repo_root, output_dir=output_dir, config_path=config, history_dir=history_dir)
    if args.output == "json":
        print(result.to_json())
    else:
        print(f"[weekly-report] Markdown: {result.metrics['markdown_report']}")
        print(f"[weekly-report] JSON: {result.metrics['json_report']}")
        if result.metrics.get("history_snapshot"):
            print(f"[weekly-report] History snapshot: {result.metrics['history_snapshot']}")
        print(f"[weekly-report] {result.advice[0]}")
    return result.exit_code()


check_docs_drift = check_docs_drift_cli
check_waivers = check_waivers_cli
report_weekly_main = report_weekly_cli

if __name__ == "__main__":
    raise SystemExit(check_adr(sys.argv[1:]))
