# Waivers Policy

This directory stores explicit, time-bound exceptions for enforced engineering controls.

Principles:
- no silent relaxation of safeguards
- every waiver is explicit, justified, and reviewable
- every waiver has an expiry date and owner

All waivers must be listed in `waivers/waivers.yml`.

Validation is enforced by:
- `tools/check_waivers.py`
- CI workflow `governance-waivers.yml`

Review ownership should be enforced using `CODEOWNERS` for:
- `waivers/**`
