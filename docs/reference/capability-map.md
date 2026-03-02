We’re building a **Runtime Guarantees Map** where:

* Everything is **ON by default** in the template.
* Turning something **OFF** requires:

  1. an explicit repo change (committed),
  2. an explicit justification (also committed),
  3. and (optionally) a visible “scar” in CI (label/approval/waiver file) so it’s not a silent downgrade.

Below is a fairly exhaustive, practical map: **Java guarantee mechanism → Python counterpart (default-on) → how to enforce opt-out with justification**.

---

## Runtime Guarantees Map: Java Mechanisms → Python Counterparts (Default ON)

| Java mechanism / guarantee                        | What it gives you                        | Python counterpart (default ON in template)                                                                       | How “OFF” must be explicit + justified                                                        |
| ------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Compilation step** (`mvn test`, `gradle build`) | Early failure, deterministic pipeline    | `make check` as single entrypoint that runs *all gates* (format, lint, type, tests, security, packaging sanity)   | Removing steps from `make check` fails CI unless waiver exists                                |
| **Static typing enforced by compiler**            | Many class of errors removed pre-runtime | `pyright` (or `mypy`) in **strict** mode in CI + pre-commit                                                       | A committed `waivers/typecheck.yml` required to relax strictness + PR must include “why”      |
| **Bytecode verification**                         | Basic safety checks before execution     | “Import hygiene gate”: no side-effects on import + module import smoke test (`python -c "import pkg"`)            | If disabled, add `waivers/import-hygiene.md` explaining why import side-effects are necessary |
| **Checked exceptions (in some APIs)**             | Explicit error paths                     | Typed error contracts + tests asserting expected exceptions; optionally `raises` checks in docs/tests             | If tests don’t cover error paths, CI requires justification in `waivers/error-contracts.md`   |
| **Final classes / immutability patterns**         | Prevents unexpected mutation             | `@dataclass(frozen=True)` where appropriate; prefer immutable value objects; lint rule for “mutable default args” | Opt-out allowed per-module with inline comment + tracked by linter “allowlist” file           |
| **Visibility modifiers** (`private/protected`)    | Encapsulation                            | Underscore convention + linting for forbidden imports (e.g., disallow `from pkg._internal import ...`)            | If internal APIs are used, require `waivers/internal-api.md` listing reasons + timeline       |
| **Package structure conventions**                 | Predictable runtime layout               | Cookiecutter skeleton with `src/` layout + enforced import paths                                                  | Changing layout requires updating `pyproject` + `make check` still must pass                  |
| **Dependency lock + Maven/Gradle resolution**     | Reproducible builds                      | Locked deps (`uv.lock` / `poetry.lock` / `requirements.lock`) + CI check that lock is up-to-date                  | If lock disabled: `waivers/lockfile.md` required; CI displays warning and blocks releases     |
| **Semantic versioning & release tooling**         | Predictable artifact evolution           | Automated versioning (e.g., Release Please / semantic-release) + changelog generation                             | If disabled: `waivers/release.md`; CI blocks tags/releases without explicit version policy    |
| **Unit tests (JUnit) as standard**                | Regression safety                        | `pytest` with coverage gate + deterministic test command                                                          | Coverage threshold changes require `waivers/coverage.yml` + PR rationale                      |
| **Integration tests profiles**                    | Runtime safety across boundaries         | `pytest -m integration` + docker-compose test env (optional)                                                      | Opt-out requires justification and an issue link; CI records “integration disabled”           |
| **Build-time annotation processing**              | Extra compile-time guarantees            | Pre-commit/CI codegen checks (OpenAPI clients, ORM models, etc.) + “generated files match” check                  | Disabling requires `waivers/codegen.md`                                                       |
| **Static analysis** (SpotBugs, Checkstyle)        | Catch risky patterns                     | `ruff` (rules-heavy), `bandit` (security), `semgrep` (optional)                                                   | Removing a rule requires editing config + `waivers/static-analysis.md`                        |
| **Formatting enforcement**                        | No style drift                           | `ruff format` (or black) in pre-commit + CI                                                                       | Formatting step cannot be disabled without `waivers/formatting.md`                            |
| **Compiler warnings as errors**                   | No ignored risk                          | “Lint warnings are errors” policy: CI fails on new lint/type issues                                               | Lowering strictness requires waiver + repo owner approval                                     |
| **Null-safety patterns** (Optional/annotations)   | Avoid NPE class                          | `Optional[T]` type discipline + `strict` typing, plus tests for `None` behavior                                   | Allowing `Any`/unchecked requires per-module allowlist + waiver entry                         |
| **Threading model discipline**                    | Predictable concurrency                  | Explicit concurrency policy: `asyncio` or threads, but not ad hoc; linting for blocking calls in async            | Waive via `waivers/concurrency.md` and add stress test note                                   |
| **JVM GC and memory tuning**                      | Predictable memory behavior              | Memory budget checks in CI (smoke perf), leak tests for long-running services, tracemalloc benchmarks             | If disabled, require `waivers/perf.md` and define monitoring in prod                          |
| **Runtime flags** (JVM args)                      | Controlled runtime                       | Standard Python runtime flags: `PYTHONHASHSEED`, `-X dev` in dev, deterministic seed for tests                    | If changed, must be committed and documented in `docs/runtime.md`                             |
| **Classpath sanity**                              | Avoid runtime class conflicts            | Dependency conflict checks (`pip check`), import graph sanity                                                     | Disabling requires `waivers/deps.md`                                                          |
| **Jar signing / provenance**                      | Trustable artifacts                      | SBOM generation (CycloneDX), provenance attestation (optional), signed tags/releases                              | If off: `waivers/provenance.md` and security owner sign-off                                   |
| **Security scanning**                             | Catch known bad deps                     | Dependency CVE scan (pip-audit/safety), secret scanning, SAST rules                                               | If off: must document risk acceptance + expiry date in waiver                                 |
| **Policy gates in CI**                            | No bypass                                | Required checks + branch protection + CODEOWNERS for waiver files                                                 | Waiver edits require specific reviewer(s)                                                     |
| **Interface stability**                           | Safer evolution                          | Contract tests for public APIs (CLI, REST, library), plus “public surface diff” tooling (optional)                | Opt-out requires `waivers/contracts.md`                                                       |
| **Runtime validation** (Bean Validation)          | Fail fast on bad inputs                  | `pydantic`/`attrs` validators at boundaries; schema validation for config/env                                     | If off: require tests proving boundary safety + waiver                                        |
| **Config typing**                                 | Predictable boot                         | Typed settings model (Pydantic Settings) + startup “config audit”                                                 | If off: must commit `docs/config.md` explaining alternatives                                  |
| **Health checks**                                 | Safer ops                                | Standard `/healthz` + readiness checks for services; CLI `--self-check`                                           | If removed: `waivers/ops.md` and define replacement observability                             |
| **Structured logging**                            | Better incident response                 | JSON logging default + correlation id middleware                                                                  | Opt-out requires `waivers/logging.md` and justification                                       |
| **Metrics & tracing**                             | Runtime visibility                       | OpenTelemetry default wiring (optional), Prometheus metrics for services                                          | If off: waiver + must list minimum monitoring set                                             |
| **Fail-fast startup**                             | Catch errors early                       | Startup self-test: imports, config validation, migrations check, dependency availability (as applicable)          | Disabling requires waiver + incident risk note                                                |
| **Backward compatibility discipline**             | Stable consumers                         | Deprecation policy + changelog + semver + “breaking change label” checks                                          | Opt-out requires explicit alternative policy                                                  |

---

## The “Explicit OFF” Mechanism (so it can’t be stealthy)

To make “OFF” painful (in a healthy way), use these governance primitives:

### 1) A `waivers/` directory that is CODEOWNED

* Any relaxation requires a committed waiver file.
* Waiver format includes: **scope, reason, risk, expiry date, reviewer**.

### 2) CI rule: if a gate is weakened, it must reference a waiver

Examples:

* lowering coverage threshold
* turning off strict typing
* disabling dependency lock enforcement
* excluding security scans

### 3) CI summary prints active waivers

So every PR shows: “Active waivers: 3”, with links.

---

## Minimal Waiver Schema (simple, strict, auditable)

You can standardize a single file like `waivers.yml`:

* `id`
* `control` (e.g., `typecheck.strict`)
* `scope` (paths/modules)
* `reason`
* `risk`
* `expires`
* `owner`
* `approvers`

Turning anything off requires adding an entry. That’s the “they need to commit it” and “they need to clarify” part, mechanically enforced.

---