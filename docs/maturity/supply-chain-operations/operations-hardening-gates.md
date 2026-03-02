# Operations Hardening Gates

## Why This Exists

These gates make operational quality visible before incidents happen.

Without explicit runtime-oriented checks, teams often discover problems only after release:
- performance regressions
- slow memory growth
- retry/recovery behavior that does not actually recover
- logs/events that are too weak to diagnose failures quickly

This lane makes those expectations executable and repeatable.

## What Is Checked

The operational gate runner is:
- `tools/run_ops_gates.py`

Invoked through:
- `make ops-gate`
- `./scripts/ops_gate.sh`

### 1) Performance gate
- Runs a deterministic micro-workload (`greet()` call loop).
- Measures elapsed and per-call latency.
- Fails if per-call latency exceeds configured threshold.

Defaults:
- `--perf-iterations 20000`
- `--perf-max-ms 0.02`

### 2) Memory leak gate
- Uses `tracemalloc` with explicit `gc.collect()` before/after workload.
- Measures retained memory growth after repeated calls.
- Fails if retained growth exceeds threshold.

Defaults:
- `--leak-iterations 25000`
- `--leak-max-growth-kb 64`

### 3) Recovery + observability gate
- Simulates a transiently failing operation.
- Validates retry-based recovery occurs within max retries.
- Emits structured events with correlation ID and verifies event integrity:
  - required event sequence includes start/retry/success
  - consistent correlation ID across all events

Default:
- `--recovery-max-retries 4`

## Output Contract

The runner emits machine-readable JSON summary with per-gate results:
- `status` (`passed` or `failed`)
- `gates[]` with gate name, pass/fail, and metrics

This allows CI and future dashboards to consume results consistently.

## CI Integration

### GitHub
- Workflow: `.github/workflows/operations-gates.yml`
- Runs on push/PR
- Installs dev dependencies, then executes `make ops-gate`

### GitLab
- Pipeline: `.gitlab-ci.yml`
- Job: `ops_gates` (`quality` stage)
- Runs on merge requests/branch pipelines (excluded on tags)

## Why This Is a Separate Lane

Default local development path (`make check`) stays fast and focused on coding feedback.

Operational gates are intentionally isolated because they represent system-readiness checks:
- they encode production-facing behavior, not just code style
- they provide stronger confidence before release or merge
- they make operational expectations explicit for all contributors

## Local Usage

Run with defaults:

```bash
make ops-gate
```

Tune thresholds for experimentation:

```bash
./scripts/ops_gate.sh --perf-max-ms 0.03 --leak-max-growth-kb 96
```

## Extension Guidance

When product behavior grows, extend this gate set with domain-specific checks:
- recovery semantics for real adapters/repositories
- structured telemetry schema validation for real runtime events
- latency SLO budgets for critical flows
- resource-bound checks for real workloads

Keep each check deterministic and explainable, and keep thresholds documented.
