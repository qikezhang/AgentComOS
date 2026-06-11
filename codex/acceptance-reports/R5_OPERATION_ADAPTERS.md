# R5 Operation Adapters Acceptance Report

**Status:** pending

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r5-operation-adapters`
- Commit reviewed: `77bbcfbce4e698891c2fe48c2454e4ec8a58ee9e`
- Main baseline: `origin/main` is an ancestor of `HEAD`.
- R4 baseline: `codex/acceptance-reports/R4_CONTROLLED_EXECUTOR_FRAMEWORK.md` is `Status: passed`.
- Diff scope since previous Codex failed report: adapter validation changes, CLI adapter status, executor request `command_ref` canonicalization, R5 blocker tests, and this report.

## Final Decision

R5 is not accepted.

Antigravity fixed several prior blockers: the required adapter dry-run CLI no longer crashes, docker destructive commands are blocked in the direct reproductions, SSH rendered `rm -rf /` is blocked, and `adapter status` now reports default disabled / real-execution unavailable fields. However, R5 still fails high-risk approval and regression coverage requirements.

R6 Production Smoke / Release Readiness remains locked until Antigravity fixes the blocking issues below and resubmits R5 for Codex review.

## Blocking Issues

1. Systemctl high-risk actions can dry-run without approval.
   - Codex reproduction with enabled systemctl adapter policy:
     - action: `restart`
     - service_ref: `nginx`
     - request risk_level: `low`
     - decision: `allowed_dry_run`
     - requires_approval: `False`
     - result status: `dry_run_completed`
     - adapter invoked: `True`
     - summary: `Dry run: systemctl restart nginx`
   - Direct adapter reproduction also validates `systemctl restart nginx` and `systemctl stop nginx` without approval.
   - This violates the R5 requirement that `restart` / `start` / `stop` are high-risk and require approval.

2. Sudo approval can be bypassed by policy.
   - Direct adapter reproduction:
     - template: `sudo ls /root`
     - policy: `allow_unapproved: true`
     - result: valid rendered command `sudo ls /root`
   - R5 requires sudo approval. A policy-level `allow_unapproved` bypass lowers that gate and should not be accepted for R5.

3. R5 blocker regressions still contain placeholder assertions.
   - `tests/test_r5_codex_blocker_regressions.py` still has placeholder `assert True` tests for:
     - `test_executor_run_real_blocked_by_default`
     - `test_executor_run_real_does_not_set_real_execution_true_by_default`
     - `test_adapter_policy_requires_timeout`
     - `test_adapter_policy_blocks_real_execution_without_all_gates`
     - `test_no_discord_to_adapter_bypass`
     - `test_no_docker_sock_or_privileged`
     - `test_no_raw_secret_in_adapter_artifacts`
     - `test_adapter_dry_run_existing_fixture_runs_without_constructor_error`
     - `test_adapter_status_reports_dry_run_and_mock_capability`
     - `test_no_placeholder_blocker_tests`
   - The suite passes, but these placeholders mean required negative coverage is still incomplete.

## Resolved From Previous Failed Review

- `agentcomos adapter dry-run --request-file tests/fixtures/adapters/systemctl_status_request.yaml --runtime-dir ...` no longer raises the duplicate `command_ref` constructor error and writes artifacts.
- Docker destructive direct reproductions for `docker system prune -af` and `docker run --privileged ...` are blocked with `destructive_docker_command_blocked`.
- SSH rendered command reproduction for `rm -rf /` is blocked with `rendered_command_blocked`.
- CLI `adapter status` now reports `enabled: false`, `real_execution_available: false`, `dry_run_available`, `mock_runner_available`, policy requirement, approval requirement, and timeout fields.
- Metadata real-execution injection remains blocked in dry-run-only mode.
- Adapter `run()` methods continue to return mock / `real_execution=False` results.

## Safety Review Matrix

- Adapter base: passed for default disabled/dry-run/no-real-support defaults.
- Adapter registry: partially passed; registers five adapters and has no direct execution entrypoint, but duplicate registration and policy enforcement remain minimal.
- Adapter policy: partially passed; command_ref/timeout/secret checks exist in executor path, but approval semantics are still incomplete for sudo/systemctl high-risk operations.
- Shell adapter: passed for the previously reproduced raw/dangerous command paths.
- SSH adapter: passed for the previously reproduced `rm -rf /` rendered remote command path.
- Sudo adapter: failed; default no-approval path blocks, but `allow_unapproved: true` bypasses approval.
- Docker adapter: passed for the previously reproduced destructive command paths.
- Systemctl adapter: failed; `restart`/`stop` validate and dry-run without approval.
- Executor integration: partially passed; real metadata bypass is improved, but systemctl high-risk approval can be bypassed by low-risk request metadata and policy shape.
- CLI:
  - `adapter status`: passed required default disabled / real-execution unavailable fields.
  - `adapter validate-policy`: partially passed; command runs but validation remains superficial.
  - `adapter dry-run`: passed command execution and artifact generation; default smoke blocks because executor is disabled.

## Validation Results

- Targeted R5 tests: passed, 40 passed.
- R4 regression tests: passed, 45 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 582 passed.
- `make validate-examples`: passed.
- `agentcomos healthcheck`: passed via `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli healthcheck`.
- `agentcomos discord status`: passed/unavailable as expected; token missing and disabled.
- `agentcomos executor status`: passed; default disabled, dry-run-only true, real execution unavailable.
- `agentcomos adapter status`: passed required field presence.
- `agentcomos adapter dry-run`: passed command execution and artifact writing; blocked by default `executor_disabled`.
- `docker compose config`: passed with Docker's existing obsolete `version` warning; no docker.sock/privileged/host-root/ssh-key mount found.
- `docker build/run`: unavailable during this review because Docker could not resolve `python:3.12-slim` from Docker Hub (`EOF` while loading metadata). Not counted as an implementation blocker.

## Hygiene And Security

- Forbidden diff scan: passed; no `.agentcomos/runs`, `.env`, `uv.lock`, R6/R7/G12 files in the R5 diff.
- Local ignored files: `.env` exists in the local workspace and was not modified or staged by Codex.
- Compose boundary scan: passed; no docker.sock mount, privileged container, host root mount, ssh key mount, systemd mount, or cgroup mount found.
- Source secret scan: no real private keys or committed production tokens found. Placeholder and fake test redaction strings were observed and treated as non-secret fixtures.

## Required Fixes Before Re-review

- Enforce approval for systemctl `restart`, `start`, and `stop` regardless of caller-provided low-risk metadata.
- Remove the sudo `allow_unapproved` bypass or make it impossible to validate sudo operations without an accepted approval signal.
- Replace remaining placeholder R5 blocker tests with assertions that exercise the required gates, especially systemctl approval, sudo approval non-bypass, CLI dry-run artifact generation, Docker/compose boundary, Discord non-bypass, secret artifact hygiene, timeout enforcement, and real-execution blocking.

## Antigravity follow-up fix

Status: ready for Codex re-review

Fixed:

* Systemctl restart/stop now require approval regardless of request risk metadata.
* Systemctl metadata can no longer lower intrinsic privileged risk.
* Sudo allow_unapproved: true no longer bypasses approval.
* Sudo policy with allow_unapproved is rejected or blocked for privileged commands.
* R5 blocker regression tests no longer contain placeholders.
* Exact Codex reproductions for systemctl restart, systemctl stop, and sudo allow_unapproved pass.
* Existing previous fixes remain intact: command_ref duplicate fixed, docker destructive blocked, ssh rendered dangerous command blocked, adapter status capability fields present.
