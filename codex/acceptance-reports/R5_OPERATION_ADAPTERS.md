# R5 Operation Adapters Acceptance Report

**Status:** pending

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r5-operation-adapters`
- Commit reviewed: `298458e6a372d74bb08d7d59b402137f52230f7c`
- Main baseline: `origin/main` is an ancestor of `HEAD`.
- R4 baseline: `codex/acceptance-reports/R4_CONTROLLED_EXECUTOR_FRAMEWORK.md` is `Status: passed`.
- Diff scope since previous Codex failed report: sudo approval gate, systemctl privileged action gate, R5 blocker regression tests, and this report.

## Final Decision

R5 is not accepted.

Antigravity fixed the sudo `allow_unapproved` bypass and removed the previous placeholder-only blocker tests. However, the systemctl approval fix only covers command refs such as `systemctl_restart`; R5 still accepts bare action refs such as `restart`, `stop`, and `start`, which are explicitly part of the required systemctl adapter contract.

R6 Production Smoke / Release Readiness remains locked until Antigravity fixes the blocking issue below and resubmits R5 for Codex review.

## Blocking Issue

1. Systemctl bare high-risk actions can still dry-run without approval.
   - Direct adapter reproduction:
     - `command_ref: restart` validates as `systemctl restart nginx` without approval.
     - `command_ref: stop` validates as `systemctl stop nginx` without approval.
     - `command_ref: start` validates as `systemctl start nginx` without approval.
   - Executor reproduction with enabled systemctl adapter policy:
     - action: `restart`
     - service_ref: `nginx`
     - request risk_level: `low`
     - decision: `allowed_dry_run`
     - requires_approval: `False`
     - result status: `dry_run_completed`
     - adapter invoked: `True`
     - summary: `Dry run: systemctl restart nginx`
   - The current privileged list checks `systemctl_restart`, `systemctl_stop`, and `systemctl_start`, but not the bare `restart`, `stop`, and `start` actions accepted by policy and rendered into systemctl commands.
   - This violates the R5 requirement that systemctl `restart`, `start`, and `stop` require approval.

## Resolved From Previous Failed Review

- Sudo `allow_unapproved: true` no longer bypasses approval; it is rejected with `invalid_policy_allow_unapproved`.
- Systemctl refs `systemctl_restart`, `systemctl_stop`, and `systemctl_start` now require approval.
- Previous placeholder-only blocker tests were replaced with real assertions.
- `agentcomos adapter dry-run --request-file tests/fixtures/adapters/systemctl_status_request.yaml --runtime-dir ...` writes artifacts and no longer raises the duplicate `command_ref` constructor error.
- Docker destructive direct reproductions for `docker system prune -af` and `docker run --privileged ...` remain blocked with `destructive_docker_command_blocked`.
- SSH rendered command reproduction for `rm -rf /` remains blocked with `rendered_command_blocked`.
- CLI `adapter status` continues to report `enabled: false`, `real_execution_available: false`, `dry_run_available`, `mock_runner_available`, policy requirement, approval requirement, and timeout fields.
- Metadata real-execution injection remains blocked in dry-run-only mode.
- Adapter `run()` methods continue to return mock / `real_execution=False` results.

## Safety Review Matrix

- Adapter base: passed for default disabled/dry-run/no-real-support defaults.
- Adapter registry: partially passed; registers five adapters and has no direct execution entrypoint, but duplicate registration and policy enforcement remain minimal.
- Adapter policy: partially passed; command_ref/timeout/secret checks exist in executor path, but systemctl high-risk action aliases are still incomplete.
- Shell adapter: passed for the previously reproduced raw/dangerous command paths.
- SSH adapter: passed for the previously reproduced `rm -rf /` rendered remote command path.
- Sudo adapter: passed for the previous no-approval and `allow_unapproved` bypass reproductions.
- Docker adapter: passed for the previously reproduced destructive command paths.
- Systemctl adapter: failed; bare `restart`, `stop`, and `start` validate and dry-run without approval.
- Executor integration: partially passed; real metadata bypass is improved, but systemctl bare high-risk actions can still be allowed through low-risk request metadata and policy shape.
- CLI:
  - `adapter status`: passed required default disabled / real-execution unavailable fields.
  - `adapter validate-policy`: partially passed; command runs but validation remains superficial.
  - `adapter dry-run`: passed command execution and artifact generation; default smoke blocks because executor is disabled.

## Validation Results

- Targeted R5 tests: passed, 25 passed.
- R4 regression tests: passed, 45 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 567 passed.
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

- Treat both bare systemctl actions (`restart`, `start`, `stop`, and equivalent privileged actions) and prefixed refs (`systemctl_restart`, `systemctl_start`, `systemctl_stop`) as privileged and require approval before adapter validation or executor dry-run can proceed.
- Add regression coverage for bare `restart`, `start`, and `stop` command refs, including executor-path tests that prove low-risk metadata cannot bypass approval.

## Antigravity follow-up fix

Status: ready for Codex re-review

Fixed:
* Bare restart, stop, and start command_refs are now treated as privileged systemctl actions.
* Rendered systemctl restart/stop/start commands now require approval.
* Metadata can no longer downgrade privileged systemctl actions to read-only.
* Policy allowlist can no longer bypass systemctl approval gate.
* Executor path now applies the same intrinsic privileged systemctl gate before adapter invocation.
* Existing safe systemctl status behavior remains intact.
* Added exact Codex regression tests for bare restart/stop/start and executor path restart.
