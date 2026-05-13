from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, cast

import yaml

from .result import GuardResult


class CoverageConfig(dict[str, Any]):
    pass


def _load_config(config_path: Path) -> CoverageConfig:
    if not config_path.exists():
        raise RuntimeError(f"coverage governance config not found: {config_path}")

    payload_obj: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if payload_obj is None:
        payload_obj = {}
    if not isinstance(payload_obj, dict):
        raise RuntimeError("coverage governance config must be a mapping")
    payload = cast(dict[str, Any], payload_obj)

    version = payload.get("version")
    if version != 1:
        raise RuntimeError("coverage governance config version must be 1")

    coverage_file = payload.get("coverage_file", "coverage.xml")
    baseline_file = payload.get("baseline_file", "tools/coverage_baseline.json")
    thresholds_obj = payload.get("thresholds", {})
    parity_obj = payload.get("parity", {})
    scope_obj = payload.get("scope", {})

    if not isinstance(coverage_file, str) or not coverage_file.strip():
        raise RuntimeError("coverage_file must be a non-empty string")
    if not isinstance(baseline_file, str) or not baseline_file.strip():
        raise RuntimeError("baseline_file must be a non-empty string")
    if not isinstance(thresholds_obj, dict):
        raise RuntimeError("thresholds must be a mapping")
    if not isinstance(parity_obj, dict):
        raise RuntimeError("parity must be a mapping")
    if not isinstance(scope_obj, dict):
        raise RuntimeError("scope must be a mapping")

    global_min = thresholds_obj.get("global_min", 0)
    package_min_obj = thresholds_obj.get("package_min", {})
    if not isinstance(global_min, (int, float)):
        raise RuntimeError("thresholds.global_min must be numeric")
    if not isinstance(package_min_obj, dict):
        raise RuntimeError("thresholds.package_min must be a mapping")

    package_min: dict[str, float] = {}
    for key, value in package_min_obj.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, (int, float)):
            raise RuntimeError("thresholds.package_min entries must map non-empty strings to numeric values")
        package_min[key] = float(value)

    enabled = parity_obj.get("enabled", True)
    max_regression_points = parity_obj.get("max_regression_points", 0.5)
    if not isinstance(enabled, bool):
        raise RuntimeError("parity.enabled must be boolean")
    if not isinstance(max_regression_points, (int, float)):
        raise RuntimeError("parity.max_regression_points must be numeric")

    include_obj = scope_obj.get("include", ["src/**"])
    exclude_obj = scope_obj.get("exclude", [])
    if not isinstance(include_obj, list) or not all(isinstance(x, str) for x in include_obj):
        raise RuntimeError("scope.include must be a list of strings")
    if not isinstance(exclude_obj, list) or not all(isinstance(x, str) for x in exclude_obj):
        raise RuntimeError("scope.exclude must be a list of strings")

    return CoverageConfig(
        {
            "version": 1,
            "coverage_file": coverage_file.strip(),
            "baseline_file": baseline_file.strip(),
            "thresholds": {
                "global_min": float(global_min),
                "package_min": package_min,
            },
            "parity": {
                "enabled": enabled,
                "max_regression_points": float(max_regression_points),
            },
            "scope": {
                "include": list(include_obj),
                "exclude": list(exclude_obj),
            },
        }
    )


def _resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    return path


def _parse_coverage_xml(coverage_file: Path) -> tuple[float, dict[str, float]]:
    if not coverage_file.exists():
        raise RuntimeError(f"coverage file not found: {coverage_file}")

    try:
        root = ET.fromstring(coverage_file.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid coverage xml: {exc}") from exc

    line_rate = root.attrib.get("line-rate")
    if line_rate is None:
        raise RuntimeError("coverage xml missing top-level line-rate")

    try:
        global_coverage = round(float(line_rate) * 100, 2)
    except ValueError as exc:
        raise RuntimeError("coverage xml has invalid top-level line-rate") from exc

    package_coverage: dict[str, float] = {}
    for package in root.findall(".//package"):
        name = package.attrib.get("name", "").strip()
        if not name:
            continue
        package_rate = package.attrib.get("line-rate")
        if package_rate is None:
            continue
        try:
            package_coverage[name] = round(float(package_rate) * 100, 2)
        except ValueError:
            continue

    return global_coverage, package_coverage


def _load_baseline(baseline_file: Path) -> dict[str, Any] | None:
    if not baseline_file.exists():
        return None
    payload_obj = json.loads(baseline_file.read_text(encoding="utf-8"))
    if not isinstance(payload_obj, dict):
        raise RuntimeError("coverage baseline must be a JSON object")
    return cast(dict[str, Any], payload_obj)


def check_coverage_governance(*, repo_root: Path, config_path: Path) -> GuardResult:
    try:
        config = _load_config(config_path)
    except RuntimeError as exc:
        return GuardResult(
            guard="coverage_governance",
            status="fail",
            violations=[{"message": str(exc)}],
        )

    coverage_file = _resolve_path(repo_root, cast(str, config["coverage_file"]))
    baseline_file = _resolve_path(repo_root, cast(str, config["baseline_file"]))

    try:
        global_coverage, package_coverage = _parse_coverage_xml(coverage_file)
    except RuntimeError as exc:
        return GuardResult(
            guard="coverage_governance",
            status="fail",
            violations=[{"message": str(exc)}],
            metrics={"coverage_file": str(coverage_file)},
        )

    thresholds = cast(dict[str, Any], config["thresholds"])
    parity = cast(dict[str, Any], config["parity"])
    package_min = cast(dict[str, float], thresholds["package_min"])
    global_min = float(thresholds["global_min"])
    violations: list[str] = []

    if global_coverage < global_min:
        violations.append(
            f"global coverage {global_coverage:.2f}% is below required minimum {global_min:.2f}%"
        )

    for package_name, minimum in sorted(package_min.items()):
        current = package_coverage.get(package_name)
        if current is None:
            violations.append(f"package coverage missing for configured package '{package_name}'")
            continue
        if current < minimum:
            violations.append(
                f"package '{package_name}' coverage {current:.2f}% is below required minimum {minimum:.2f}%"
            )

    baseline_present = False
    regression_points = 0.0
    if bool(parity["enabled"]):
        try:
            baseline = _load_baseline(baseline_file)
        except (RuntimeError, json.JSONDecodeError) as exc:
            return GuardResult(
                guard="coverage_governance",
                status="fail",
                violations=[{"message": f"invalid coverage baseline: {exc}"}],
                metrics={"baseline_file": str(baseline_file)},
            )
        if baseline is not None:
            baseline_present = True
            previous_global = baseline.get("global_coverage")
            if isinstance(previous_global, (int, float)):
                regression_points = round(float(previous_global) - global_coverage, 2)
                if regression_points > float(parity["max_regression_points"]):
                    violations.append(
                        "coverage regression exceeds allowed maximum: "
                        f"baseline={float(previous_global):.2f}%, current={global_coverage:.2f}%, "
                        f"regression={regression_points:.2f} points, allowed={float(parity['max_regression_points']):.2f}"
                    )

    result = GuardResult(
        guard="coverage_governance",
        status="fail" if violations else "pass",
        violations=[{"message": item} for item in violations],
        metrics={
            "coverage_file": str(coverage_file),
            "baseline_file": str(baseline_file),
            "global_coverage": global_coverage,
            "package_coverage": package_coverage,
            "baseline_present": baseline_present,
            "regression_points": regression_points,
        },
    )
    if not baseline_present and bool(parity["enabled"]):
        result.advice.append("Coverage baseline not found; parity check skipped.")
    return result


def format_coverage_governance_result(result: GuardResult) -> str:
    if result.status == "fail":
        lines = ["[coverage-governance] Violations:"]
        lines.extend(f"  - {item['message']}" for item in result.violations)
        return "\n".join(lines)
    line = (
        "[coverage-governance] OK "
        f"(global={float(result.metrics.get('global_coverage', 0.0)):.2f}%, "
        f"baseline_present={bool(result.metrics.get('baseline_present', False))}, "
        f"regression={float(result.metrics.get('regression_points', 0.0)):.2f})"
    )
    if result.advice:
        return line + f"\n[coverage-governance] {result.advice[0]}"
    return line


def run_coverage_governance_check(*, repo_root: Path, config_path: Path) -> int:
    result = check_coverage_governance(repo_root=repo_root, config_path=config_path)
    print(format_coverage_governance_result(result))
    return result.exit_code()
