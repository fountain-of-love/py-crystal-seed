# Coverage Governance Guardrail

Purpose:
- treat coverage as governed confidence, not a raw percentage
- block regressions below agreed thresholds
- make coverage drift visible in governance reporting

## Enforced By

- `guardrails-governance`
- local wrapper: `tools/check_coverage_governance.py`
- config: `tools/coverage_governance.yml`

## Policy

The guard validates:
- global coverage minimum
- configured package-level minimums
- optional regression parity against a stored baseline

A missing `coverage.xml` is a hard failure for the guard itself.
A missing baseline is not a hard failure; parity is skipped and reported explicitly.

## Output

- text output for local development
- JSON output through `GuardResult`
- weekly report summary via `guardrails-report-weekly`

## Commands

```bash
./venv/bin/python ./tools/check_coverage_governance.py
make coverage-governance
```
