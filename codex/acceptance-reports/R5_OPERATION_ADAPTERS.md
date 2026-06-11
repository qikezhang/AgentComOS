# R5 Operation Adapters Acceptance Report

**Status:** passed

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r5-operation-adapters`
- Commit reviewed: `3c0981ef1a2fac792ac99d41e891fe8ee6286311`
- Main baseline: `origin/main` is an ancestor of `HEAD`.
- R4 baseline: `codex/acceptance-reports/R4_CONTROLLED_EXECUTOR_FRAMEWORK.md` is `Status: passed`.
- Diff scope since previous Codex failed report: systemctl privileged action detection, executor systemctl approval gate, R5 blocker regression tests, and this report.

## Final Decision

R5 is accepted.

The previous blocking issue is resolved: bare systemctl actions `restart`, `stop`, and `start` now require approval, and the executor path returns `requires_approval` without invoking the adapter for those actions when approval is absent.

R5 may be merged to `main`. R6 Production Smoke / Release Readiness may begin after R5 is merged.

## Resolved Blockers

- Bare systemctl privileged actions are blocked without approval:
  - `restart` -> `privileged_approval_required`
  - `stop` -> `privileged_approval_required`
  - `start` -> `privileged_approval_required`
  - `reload`, `enable`, and `disable` are also treated as privileged.
- Prefixed systemctl refs remain blocked without approval:
  - `systemctl_restart`
  - `systemctl_stop`
  - `systemctl_start`
- Executor path for bare `restart`, `stop`, and `start` returns:
  - decision: `requires_approval`
  - requires_approval: `True`
  - reason: `privileged_approval_required`
  - result status: `requires_approval`
  - adapter_invoked: `False`
- Safe read-only systemctl status remains allowed through adapter dry-run.
- Sudo `allow_unapproved: true` remains blocked with `invalid_policy_allow_unapproved`.
- Docker destructive commands remain blocked.
- SSH rendered destructive commands remain blocked.
- Adapter status reports disabled/default-no-real-execution fields.
- Required adapter dry-run CLI writes artifacts and no longer fails on duplicate `command_ref`.

## Safety Review Matrix

- Adapter base: passed for default disabled/dry-run/no-real-support defaults.
- Adapter registry: passed for registered shell, ssh, sudo, docker, and systemctl adapters with no direct execution entrypoint.
- Adapter policy: passed for missing policy, disabled adapter, command_ref allowlist, deny override, timeout, secret request, and real-execution default-deny paths covered in executor/adapters.
- Shell adapter: passed for raw/dangerous command blocking and mock/dry-run-only behavior.
- SSH adapter: passed for host allowlist and rendered dangerous command blocking.
- Sudo adapter: passed for required approval and `allow_unapproved` non-bypass.
- Docker adapter: passed for destructive command blocking including system prune and privileged run.
- Systemctl adapter: passed for service/action allowlist, status dry-run, and approval-required privileged actions.
- Executor integration: passed for R4-controlled decision path, adapter non-bypass, dry-run default, real-execution denial, and systemctl privileged action approval gate.
- CLI:
  - `adapter status`: passed required default disabled / real-execution unavailable fields.
  - `adapter validate-policy`: passed command execution; validation remains intentionally shallow in this R5 implementation.
  - `adapter dry-run`: passed command execution and artifact generation; default smoke blocks because executor is disabled.

## Validation Results

- Targeted R5 tests: passed, 37 passed.
- R4 regression tests: passed, 45 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 579 passed.
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
- Generated adapter dry-run artifact secret grep: passed for raw token/private-key/password/api_key patterns.

## Residual Notes

- The R4/R5 request model still uses `requires_approval` as a coarse approval-related field, while privileged adapters also check `metadata.approved`. This should be clarified in a future schema/spec cleanup, but it does not block R5 because unapproved privileged systemctl paths now return blocked/requires_approval and do not complete.
- `adapter validate-policy` remains a structural status command rather than a deep policy linter. R6 may add stronger policy linting, but R5 safety gates are enforced at executor/adapter evaluation time.
