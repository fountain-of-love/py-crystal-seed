# Operations Hardening Guardrail

## Purpose

Make runtime-quality expectations executable before release:
- performance budgets
- memory growth/leak limits
- recovery behavior under transient failures
- observability signal integrity

## Enforcement

Primary runner:
- `tools/run_ops_gates.py`

Primary command:
- `make ops-gate`

Combined hardening command:
- `make hardening-check`

## What It Checks

1. Performance gate
- deterministic micro-workload latency
- threshold-based pass/fail

2. Memory gate
- retained allocation growth via `tracemalloc`
- threshold-based pass/fail

3. Recovery + observability gate
- retry-based recovery from transient failure
- structured event sequence validation
- correlation ID consistency validation

## CI Integration

GitHub:
- `.github/workflows/operations-gates.yml`

GitLab:
- `.gitlab-ci.yml` -> `ops_gates`

## Policy Intent

This guardrail is kept separate from the fast developer loop (`make check`) so teams keep fast feedback while still enforcing production-facing reliability standards.
