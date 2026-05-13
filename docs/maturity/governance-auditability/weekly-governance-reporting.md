# Weekly Governance Reporting

Purpose:
- produce a weekly governance snapshot and trend artifact
- make the guardrail system itself observable over time

## Enforced By

- `guardrails-report-weekly`
- config: `tools/weekly_reporting.yml`

## Output

Artifacts:
- `artifacts/governance/weekly-report.md`
- `artifacts/governance/weekly-report.json`
- `artifacts/governance/history/weekly-report-*.json`

## Includes

- per-guard status summaries
- guard package versions
- waiver counts
- coverage summary when enabled
- maturity-evidence summary when enabled
- trend deltas when prior history exists

## CI

GitLab scheduled pipeline job:
- `weekly_governance_report`

The report is advisory and always emits artifacts.
