# Maturity Evidence Guardrail

Purpose:
- require explicit governance evidence when production code changes
- prevent architecture and behavior drift from landing without narrative or record

## Enforced By

- `guardrails-governance`
- local wrapper: `tools/check_maturity_evidence.py`
- config: `tools/maturity_evidence.yml`
- governance log: `governance/governance_log.yml`

## Accepted Evidence

One evidence source is sufficient by default:
- ADR update
- roadmap update
- governance log entry
- explicit governed exception marker

## Policy

The guard:
- detects changed production files from git diff
- filters them through configured production and exclusion paths
- checks whether at least one allowed evidence source exists in the same change set

If no production files changed, the guard passes in skipped mode.
If production files changed and no evidence is present, the guard fails.

## Commands

```bash
./venv/bin/python ./tools/check_maturity_evidence.py
make maturity-evidence
```
