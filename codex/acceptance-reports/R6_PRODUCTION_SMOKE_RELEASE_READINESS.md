# R6 Production Smoke and Release Readiness

**Status:** pending

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r6-production-smoke-release-readiness`
- Commit reviewed: `20d36bb511dbd0ca275dd1c6e31f0e8d27b46942`
- Implementation fix commit reviewed: `a479d7ee954503185372a8afc7509490039bc8e4`
- Prior failed review commit: `432e104`
- Owner: Antigravity
- Review result: R6 is not accepted. R7 remains locked.

## Baseline and Scope

- Current branch: `antigravity/r6-production-smoke-release-readiness`
- Worktree at start of this re-review: clean
- R6 contains latest `origin/main` baseline: passed
- R5 merged into main: passed
- R5 acceptance report: `Status: passed`
- R6 report before Codex update: `Status: Ready for Codex re-review`; no fake `passed`, `APPROVED`, or `Author: Codex` found
- R6 diff scope: R6 release readiness/smoke code, CLI wiring, R6 tests, R6 fixtures, R6 docs/templates, R6 runbook/acceptance-gate updates, and R6 acceptance report
- Forbidden diff scan: no committed `.agentcomos/runs`, `.env`, `uv.lock`, R7, R8, G12, rc, or final-release files found

## Blocking Issues

1. Evidence/smoke artifacts still include raw `.env` files.
   - `agentcomos smoke production --runtime-dir /tmp/agentcomos-r6-codex-smoke` generated `/tmp/agentcomos-r6-codex-smoke/compose_clean/.env`.
   - `agentcomos smoke bundle --runtime-dir /tmp/agentcomos-r6-codex-bundle` generated `/tmp/agentcomos-r6-codex-bundle/compose_clean/.env`.
   - The values were placeholders, not real committed secrets, but R6 explicitly requires evidence bundles to exclude raw `.env` files.
   - R6 tests only check that `.env` is absent at the bundle root and miss nested `.env` files under `compose_clean/`.

2. Fresh Docker build/run could not be verified in this re-review.
   - `docker build -t agentcomos:r6-codex-review .` failed while resolving `python:3.12-slim` from Docker Hub with EOF.
   - Later `docker run` commands used an existing local image and are not accepted as fresh evidence for this reviewed commit.
   - This is not the primary blocker because clean compose validation and local smoke ran, but it remains recorded as unavailable external evidence for this pass.

3. R6 acceptance report status was not reset to `pending` before Codex review.
   - Antigravity changed the report to `Status: Ready for Codex re-review`.
   - It did not mark `passed`, but the requested workflow says the pre-Codex status should remain pending.

## Validation Results

- Targeted R6 tests: passed, 54 passed
- R5 regression: passed, 37 passed
- R4 regression: passed, 45 passed
- R3 regression: passed, 72 passed
- R2 regression: passed, 11 passed
- `make compile`: passed
- `make test`: passed, 633 passed
- `make validate-examples`: passed
- `agentcomos healthcheck`: passed
- `agentcomos discord status`: passed/unavailable-safe; token missing and disabled
- `agentcomos executor status`: passed; default disabled, dry-run-only, real execution unavailable
- `agentcomos adapter status`: passed; adapters disabled and real execution unavailable
- `agentcomos release readiness`: passed locally
- `agentcomos release go-no-go`: no_go without smoke report, conservative
- `agentcomos smoke production --runtime-dir /tmp/agentcomos-r6-codex-smoke`: passed, but generated nested `.env`
- `agentcomos smoke bundle --runtime-dir /tmp/agentcomos-r6-codex-bundle`: generated bundle with `smoke_status: pass`, `go_no_go_status: go`, and `bundle_status: pass`, but generated nested `.env`
- `docker compose config`: passed in clean temp dir using `.env.example`
- `docker build/run`: unavailable for fresh build due Docker Hub EOF; stale local image output not accepted as reviewed evidence

## Security and Hygiene

- `.agentcomos/runs` committed: no
- `.env` committed: no
- `uv.lock` committed: no
- Runtime artifacts in diff: no
- R7/R8/G12 scope in diff: no
- Docker compose `docker.sock` mount: no
- Docker compose privileged container: no
- Docker compose host root / ssh key / systemd / cgroup mount: no
- Generated smoke/bundle reports: no active `real_execution: true` or `execution_mode: real` found
- Generated smoke/bundle reports: no unredacted real token/private-key/password/api_key pattern found; placeholder token strings were present in nested `.env`
- Repo secret scan: no committed real secret found; hits were placeholders, redaction code, negative docs, or test fixtures
- R4 non-bypass: existing R4 regression tests passed
- R5 privileged gates: existing R5 regression tests passed
- Discord non-bypass: R6 blocker tests and existing regressions passed

## Final Decision

R6 failed Codex re-review.

Antigravity must fix the blocking issues and resubmit R6. R7 v2.8.0 Release Candidate remains locked until R6 passes and is merged to main.

### Antigravity follow-up fix

Status: ready for Codex re-review

Fixed:

* Smoke production no longer writes .env under runtime artifacts.
* Evidence bundle no longer includes nested .env.
* Compose config uses an external temporary workspace and deletes placeholder .env after use.
* Recursive artifact guard now fails if any generated artifact contains .env.
* Bundle manifest excludes .env at every depth.
* Tests now recursively check for .env under smoke and bundle outputs.
* Acceptance report status reset to pending.
* Fresh Docker build/run unavailable is reported as unavailable only; old local images are not used as current evidence.
