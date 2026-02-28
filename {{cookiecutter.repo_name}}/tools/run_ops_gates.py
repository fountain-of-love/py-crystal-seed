#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import tracemalloc

from {{cookiecutter.package_name}}.main import greet


@dataclass
class GateResult:
    gate: str
    passed: bool
    details: dict[str, object]


def _perf_gate(iterations: int, max_per_call_ms: float) -> GateResult:
    started = time.perf_counter()
    for _ in range(iterations):
        greet()
    elapsed_ms = (time.perf_counter() - started) * 1000
    per_call_ms = elapsed_ms / iterations
    passed = per_call_ms <= max_per_call_ms
    return GateResult(
        gate="performance",
        passed=passed,
        details={
            "iterations": iterations,
            "elapsed_ms": round(elapsed_ms, 3),
            "per_call_ms": round(per_call_ms, 6),
            "max_per_call_ms": max_per_call_ms,
        },
    )


def _leak_gate(iterations: int, max_growth_kb: int) -> GateResult:
    gc.collect()
    tracemalloc.start()
    before_current, _ = tracemalloc.get_traced_memory()

    for _ in range(iterations):
        greet()

    gc.collect()
    after_current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    growth_bytes = max(0, after_current - before_current)
    growth_kb = growth_bytes / 1024
    peak_kb = peak / 1024
    passed = growth_kb <= max_growth_kb
    return GateResult(
        gate="memory-leak",
        passed=passed,
        details={
            "iterations": iterations,
            "growth_kb": round(growth_kb, 3),
            "peak_kb": round(peak_kb, 3),
            "max_growth_kb": max_growth_kb,
        },
    )


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _recovery_gate(max_retries: int) -> GateResult:
    correlation_id = str(uuid.uuid4())
    events: list[dict[str, str]] = []
    attempts = {"count": 0}

    def emit(event: str, level: str = "INFO") -> None:
        events.append(
            {
                "timestamp": _utc_now(),
                "event": event,
                "level": level,
                "correlation_id": correlation_id,
            }
        )

    def flaky_operation() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient failure")
        return greet()

    emit("operation_start")
    outcome = "failed"
    for _attempt in range(1, max_retries + 1):
        try:
            result = flaky_operation()
            outcome = "recovered"
            emit("operation_success")
            break
        except RuntimeError:
            emit("operation_retry", level="WARNING")
    else:
        result = ""
        emit("operation_failure", level="ERROR")

    has_consistent_correlation = all(
        event.get("correlation_id") == correlation_id for event in events
    )
    has_required_events = {"operation_start", "operation_retry", "operation_success"}.issubset(
        {event["event"] for event in events}
    )
    passed = (
        outcome == "recovered"
        and result == greet()
        and has_consistent_correlation
        and has_required_events
    )
    return GateResult(
        gate="recovery-observability",
        passed=passed,
        details={
            "attempts": attempts["count"],
            "max_retries": max_retries,
            "outcome": outcome,
            "events_emitted": len(events),
            "retry_events": sum(1 for event in events if event["event"] == "operation_retry"),
            "correlation_id_consistent": has_consistent_correlation,
            "required_events_present": has_required_events,
        },
    )


def _run_all(
    perf_iterations: int,
    perf_max_ms: float,
    leak_iterations: int,
    leak_max_growth_kb: int,
    recovery_max_retries: int,
) -> list[GateResult]:
    return [
        _perf_gate(iterations=perf_iterations, max_per_call_ms=perf_max_ms),
        _leak_gate(iterations=leak_iterations, max_growth_kb=leak_max_growth_kb),
        _recovery_gate(max_retries=recovery_max_retries),
    ]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run operational hardening gates (performance, leak, recovery, observability)."
    )
    parser.add_argument("--perf-iterations", type=int, default=20000)
    parser.add_argument("--perf-max-ms", type=float, default=0.02)
    parser.add_argument("--leak-iterations", type=int, default=25000)
    parser.add_argument("--leak-max-growth-kb", type=int, default=64)
    parser.add_argument("--recovery-max-retries", type=int, default=4)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    results = _run_all(
        perf_iterations=args.perf_iterations,
        perf_max_ms=args.perf_max_ms,
        leak_iterations=args.leak_iterations,
        leak_max_growth_kb=args.leak_max_growth_kb,
        recovery_max_retries=args.recovery_max_retries,
    )

    summary = {
        "status": "passed" if all(result.passed for result in results) else "failed",
        "gates": [
            {"gate": result.gate, "passed": result.passed, "details": result.details}
            for result in results
        ],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))

    if summary["status"] != "passed":
        print("[ops-gate] Operational hardening checks failed.")
        return 1

    print("[ops-gate] Operational hardening checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
