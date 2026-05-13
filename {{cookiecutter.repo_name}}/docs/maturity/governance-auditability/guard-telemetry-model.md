# Guard Telemetry Model

Purpose:
- define the minimum observable data produced by governance reporting

## Current Telemetry

Each weekly report carries:
- guard name
- status
- metrics
- violations
- warnings
- advice

Top-level report fields:
- `generated_at`
- `guard_versions`
- `guard_summaries`
- `trend`
- `summary`
- `advice`

## Current Trend Signals

- previous guard status
- status change flag
- waiver deltas
- coverage deltas when available

## Future Extensions

- runtime duration per guard
- pass-rate trends
- false-positive and bypass trend summaries
