# Version Evolution Guardrail

## Why This Matters (Agentic Coding Pain Point)

One of the highest-risk agentic coding failure modes is **silent cross-version drift**:
- an agent imports internals from a previous version because it is convenient
- or an agent changes shared core behavior that older versions already rely on

Both can look harmless in a local diff while creating hard-to-diagnose regressions.

This project treats that as a first-class governance problem and enforces it with a deterministic guardrail.

## Policy Enforced

The guardrail encodes two architectural rules:

### 1) Cross-Version Import Rule
- Allowed: `vN -> core.*`
- Allowed: `vN -> facade of v(N-1)` (evolution chain)
- Forbidden: `vN -> internals of v(N-1)`

### 2) Compatibility Rule (Hard Rule)
- If `v(N-1)` uses a core function/class, `vN` must treat that contract as stable.
- `vN` must extend/wrap/subclass instead of changing existing lower-rung-used contracts in place.

## Guardrail Implementation

Checker:
- `tools/check_version_import_boundaries.py`

Contract snapshot:
- `tools/version_evolution_contracts.json`

What the checker does:
1. Scans version modules and fails forbidden previous-version internal imports.
2. Detects core symbols used by lower versions.
3. Compares current signatures of those symbols to the contract snapshot.
4. Fails on contract drift (removed/renamed/changed protected symbols).

## Operational Workflow

Normal validation:

```bash
make smoke
```

This already executes the evolution checker.

Intentional contract refresh (only when compatibility policy allows and changes are reviewed):

```bash
./venv/bin/python ./tools/check_version_import_boundaries.py --write-contract
```

Then:
1. Explain why contract refresh is safe in PR notes.
2. Add migration/compatibility notes if behavior is intentionally changed.
3. Get explicit human review before merge.

## Failure Examples

### A) Forbidden previous-version internal import

Example (forbidden):

```python
import demo_pkg.versions.v5.spine
```

Expected result:
- guard fails with `[import-boundary]` violation.

### B) Protected core contract drift

Example:
- baseline contract has `api::make_run` as `func[name]`
- code changes it to `func[name,status]`

Expected result:
- guard fails with `[compatibility] contract drift`.

## Why This Removes “Overhead” Feeling

This guardrail converts abstract architecture guidance into executable checks:
- agents get immediate, precise failure reasons
- reviewers do not need to manually reconstruct version-evolution safety
- teams can move faster with less fear of hidden cross-version breakage

This is not extra ceremony. It is a safety boundary that keeps autonomous changes trustworthy.

## Recommended Team Practice

For repositories with versioned architecture:
1. Keep this guard in smoke checks.
2. Treat contract refresh as an explicit architecture event.
3. Require human approval for contract refresh diffs.
4. Keep docs/version notes updated in the same change.
