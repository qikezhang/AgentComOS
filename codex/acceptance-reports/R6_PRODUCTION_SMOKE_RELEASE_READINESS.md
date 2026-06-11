# R6 Production Smoke and Release Readiness

**Status:** failed

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r6-production-smoke-release-readiness`
- Commit reviewed: `89070a340bc0da0d9da946de47966749763b8f16`
- Owner: Antigravity
- Review result: R6 is not accepted. R7 remains locked.

## Baseline and Scope

- Current branch: `antigravity/r6-production-smoke-release-readiness`
- Worktree before review report update: clean
- R6 contains latest `origin/main` baseline: passed
- R5 merged into main: passed
- R5 acceptance report: `Status: passed`
- Diff scope: limited to R6 release readiness/smoke code, CLI wiring, R6 tests, R6 fixtures, R6 docs/templates, and this R6 acceptance report
- Forbidden diff scan: no `.agentcomos/runs`, `.env`, `uv.lock`, R7, R8, G12, rc, or final-release files found
- Initial R6 report status: `pending`; no `Status: passed`, `APPROVED`, or fake Codex approval found

## Blocking Issues

1. R6 readiness is not a complete release gate and can pass without required evidence.
   - `agentcomos release readiness` returned `status: pass` with `blockers: []` even though no regression evidence, smoke evidence bundle, command output summary, Docker build/run result, boundary scan summary, or rollback readiness artifact was required as input.
   - This violates the R6 requirement that readiness must not pass when required evidence is missing.

2. R6 go/no-go and evidence bundle are too shallow for release approval.
   - `evaluate_go_no_go()` only checks readiness status, smoke status, and readiness blockers.
   - The generated bundle contains `release_readiness_report.yaml`, `production_smoke_report.yaml`, `go_no_go_report.yaml`, and `manifest.yaml`, but omits required evidence such as R2-R5 report references, command output summaries, boundary scan summary, repo secret scan summary, regression test summary, rollback readiness summary, timestamp, and explicit Docker build/run availability.
   - `agentcomos smoke bundle` produced `go_no_go_status: go` from these incomplete self-generated reports.

3. R6 production smoke introduces raw shell execution surfaces.
   - `src/agentcomos/production_smoke.py` uses `os.popen()` for healthcheck, Discord status, executor status, adapter status, Docker compose config, and git metadata.
   - The adapter dry-run command interpolates `runtime_dir` directly into a shell string without quoting.
   - `src/agentcomos/release_readiness.py` also uses `os.popen("git ls-files")`.
   - This violates the no raw command / no new unsafe execution surface boundary for R6.

4. R6 production smoke is incomplete.
   - It does not perform Docker build/run smoke and therefore cannot correctly record build/run success versus external unavailability.
   - It does not perform a repo-wide secret scan, artifact scan, or boundary scan.
   - It does not run a separate executor dry-run safe fixture.
   - It relies on output substring checks and does not capture exit codes or stderr.
   - The CLI default runtime directory is `.agentcomos/runs/smoke`, which can dirty the repo when `--runtime-dir` is omitted.

5. R6 tests do not cover required negative and boundary cases.
   - Placeholder-only tests remain in `tests/test_r6_codex_blocker_regressions.py`:
     - `test_r6_preserves_r5_privileged_gates`
     - `test_r6_preserves_r4_redaction_semantics`
     - `test_r6_no_discord_adapter_bypass`
   - Missing required negative coverage includes missing evidence, report not passed, `.env` tracked, docker.sock mount, privileged container, real secret leakage, Docker unavailable/network EOF handling, Discord non-bypass, request metadata non-escalation, raw command blocking, and no real execution defaults.

6. Documentation acceptance gate was not updated for R6.
   - R6 added release docs, but no R6 acceptance criterion was added to `docs/18_ACCEPTANCE_GATES.md`, contrary to the repository acceptance rules.

## Validation Results

- Targeted R6 tests: passed under `.venv`, 15 passed; not acceptance-sufficient because of placeholder and missing negative tests
- R5 regression: passed, 37 passed
- R4 regression: passed, 45 passed
- R3 regression: passed, 72 passed
- R2 regression: passed, 11 passed
- `make compile`: passed
- `make test`: passed, 594 passed
- `make validate-examples`: passed
- `agentcomos healthcheck`: passed
- `agentcomos discord status`: passed/unavailable-safe; token missing and disabled
- `agentcomos executor status`: passed; default disabled, dry-run-only, real execution unavailable
- `agentcomos adapter status`: passed; adapters disabled and real execution unavailable
- `agentcomos release readiness`: command ran, but gate failed review because it passed with missing/incomplete evidence
- `agentcomos release go-no-go`: command ran; returned `no_go` without smoke report, but overall implementation failed review because bundle can produce `go` from incomplete evidence
- `agentcomos smoke production --runtime-dir /tmp/agentcomos-r6-codex-smoke`: command ran and generated a report, but implementation failed review for incomplete smoke coverage and raw shell execution
- `agentcomos smoke bundle --runtime-dir /tmp/agentcomos-r6-codex-bundle`: command ran and generated files, but evidence bundle failed review for missing required contents
- `docker compose config`: passed with Docker's obsolete `version` warning
- `docker build/run`: unavailable because Docker Hub metadata resolution returned EOF; not treated as the primary blocker, but R6 smoke does not model build/run availability correctly

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
- Generated smoke/bundle reports: no unredacted token/private-key/password/api_key pattern found
- Repo secret scan: no real secret found; hits were placeholders, redaction code, negative docs, or test fixtures
- R4 non-bypass: existing R4 regression tests passed
- R5 privileged gates: existing R5 regression tests passed
- Discord non-bypass: not acceptance-proven by R6 because the R6 blocker regression test is a placeholder

## Final Decision

R6 failed Codex review.

Antigravity must fix the blocking issues and resubmit R6. R7 v2.8.0 Release Candidate remains locked until R6 passes and is merged to main.
