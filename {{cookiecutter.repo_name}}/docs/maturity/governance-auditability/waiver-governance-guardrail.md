# Waiver Governance Guardrail

## Purpose

Allow explicit exceptions without losing accountability or lifecycle control.

## Enforcement

Checker:
- `tools/check_waivers.py`

Command:
- `make waivers-check`

Registry:
- `waivers/waivers.yml`

## Rules Enforced

1. Schema validity
- required fields must be present and well-formed.

2. Expiry discipline
- expiry dates must be valid and non-expired.

3. Ownership/approval metadata
- approvers and ownership metadata must be present and usable.

4. Lifecycle visibility
- active and expiring waivers are reported for governance visibility.

## CI Integration

GitHub:
- `.github/workflows/governance-waivers.yml`

GitLab:
- can be integrated into governance lanes via `make waivers-check`.

## Policy Intent

Waivers are controlled exceptions with expiration and accountability, not permanent bypasses.
