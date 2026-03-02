from __future__ import annotations

import gc
import json
import time
import tracemalloc
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class GateResult:
    gate: str
    passed: bool
    details: dict[str, object]


def _perf_gate(
    *,
    greet_fn: Callable[[], str],
    iterations: int,
    max_per_call_ms: float,
) -> GateResult:
    started = time.perf_counter()
    for _ in range(iterations):
        greet_fn()
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


def _leak_gate(
    *,
    greet_fn: Callable[[], str],
    iterations: int,
    max_growth_kb: int,
) -> GateResult:
    gc.collect()
    tracemalloc.start()
    before_current, _ = tracemalloc.get_traced_memory()

    for _ in range(iterations):
        greet_fn()

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


def _recovery_gate(*, greet_fn: Callable[[], str], max_retries: int) -> GateResult:
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
        return greet_fn()

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
        and result == greet_fn()
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


def run_ops_gates(
    *,
    greet_fn: Callable[[], str],
    perf_iterations: int,
    perf_max_ms: float,
    leak_iterations: int,
    leak_max_growth_kb: int,
    recovery_max_retries: int,
) -> int:
    results = [
        _perf_gate(greet_fn=greet_fn, iterations=perf_iterations, max_per_call_ms=perf_max_ms),
        _leak_gate(greet_fn=greet_fn, iterations=leak_iterations, max_growth_kb=leak_max_growth_kb),
        _recovery_gate(greet_fn=greet_fn, max_retries=recovery_max_retries),
    ]

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
