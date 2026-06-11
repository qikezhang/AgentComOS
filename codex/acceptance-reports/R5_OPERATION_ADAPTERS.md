# R5 Operation Adapters Acceptance Report

**Status:** failed

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r5-operation-adapters`
- Commit reviewed: `36922f530ba646a2a38fac245b5694c7950bd356`
- Main baseline: `origin/main` is an ancestor of `HEAD`.
- R4 baseline: `codex/acceptance-reports/R4_CONTROLLED_EXECUTOR_FRAMEWORK.md` is `Status: passed`.
- Diff scope since previous Codex failed report: adapter validation changes, executor real-execution gating changes, executor request `command_ref` handling, R5 blocker tests, and this report.

## Final Decision

R5 is not accepted.

Antigravity fixed part of the previous real-execution semantics issue: metadata real-execution injection no longer reaches a real result in dry-run-only mode, and adapter `run()` methods now return mock/real-execution-false results. However, R5 still fails required CLI and adapter safety gates.

R6 Production Smoke / Release Readiness remains locked until Antigravity fixes the blocking issues below and resubmits R5 for Codex review.

## Blocking Issues

1. Required adapter dry-run CLI smoke is broken.
   - Command: `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli adapter dry-run --request-file tests/fixtures/adapters/systemctl_status_request.yaml --runtime-dir /tmp/agentcomos-r5-codex-adapter-dry`
   - Result: Typer error: `ExecutorRequest() got multiple values for keyword argument 'command_ref'`.
   - Cause: `ExecutorRequest.from_dict()` passes `command_ref=redacted_data.get("command_ref")` while also expanding `**redacted_data.get("metadata", {})`; fixture metadata contains `command_ref`.
   - This fails the R5 requirement that `agentcomos adapter dry-run --request-file ... --runtime-dir ...` runs through R4 evaluation and writes artifacts.

2. Docker adapter still allows explicitly forbidden destructive commands.
   - Codex reproduction with enabled docker adapter policy and allowlisted command:
     - template: `docker system prune -af`
     - decision: `allowed_dry_run`
     - result status: `dry_run_completed`
     - adapter invoked: `True`
     - summary: `Dry run: docker system prune -af`
   - `DockerAdapter.validate_request()` still only checks command_ref allowlist and template presence, then returns valid rendered command.
   - This violates the R5 requirement that `docker system prune` is blocked.

3. Sudo adapter does not enforce approval or sudo-specific safety.
   - Codex reproduction with enabled sudo adapter policy and allowlisted command:
     - template: `sudo ls /root`
     - decision: `allowed_dry_run`
     - result status: `dry_run_completed`
     - adapter invoked: `True`
     - summary: `Dry run: sudo ls /root`
   - `SudoAdapter.validate_request()` does not enforce approval and does not block raw sudo command templates beyond command_ref allowlisting.
   - This violates the R5 requirement that sudo approval is required and raw/bare sudo execution is blocked.

4. SSH adapter still permits dangerous rendered remote commands if the host is allowlisted.
   - Direct adapter reproduction:
     - host_ref: `prod`
     - template: `{x}`
     - params: `{"x": "rm -rf /"}`
     - result: valid rendered command `ssh root@prod 'rm -rf /'`
   - `SshAdapter.validate_request()` does not apply the shell adapter's rendered-command safety scan to remote commands.
   - This violates the R5 requirements that raw SSH is blocked and that unsafe commands cannot be passed to SSH.

5. CLI `adapter status` still omits required safety fields.
   - Output includes only `type`, `supports_dry_run`, and `supports_real_run`.
   - It does not report per-adapter `enabled: false` or `real_execution_available: false`.
   - This leaves the required default-disabled/default-no-real-execution posture unverifiable from the CLI.

6. R5 blocker regressions remain incomplete.
   - `tests/test_r5_codex_blocker_regressions.py` still contains placeholder `pass` tests for `executor run-real`, timeout policy, real-execution gates, Discord non-bypass, docker.sock/privileged checks, and adapter artifact secret checks.
   - Existing R5 targeted tests pass, but they do not cover the failing docker/sudo/ssh adapter paths above or the broken required CLI dry-run fixture path.

## Resolved From Previous Failed Review

- Metadata real-execution injection under `CONTROLLED_EXECUTOR_DRY_RUN_ONLY=true` no longer reaches a real execution result.
- Adapter `run()` methods no longer report `real_execution=True` for successful mock paths.
- Shell adapter now blocks the previously reproduced `rm -rf /` template parameter path.

## Safety Review Matrix

- Adapter base: passed for default disabled/dry-run/no-real-support defaults.
- Adapter registry: partially passed; registers five adapters and has no direct execution entrypoint, but duplicate registration and policy enforcement remain minimal.
- Adapter policy: partially passed; deny overrides allow now exists, command_ref/timeout/secret checks exist in executor path, but policy coverage is still not consistently enforced inside adapters.
- Shell adapter: partially passed; previous `rm -rf /` reproduction is blocked, but safety logic is not shared by other command-rendering adapters.
- SSH adapter: failed; dangerous rendered remote commands can validate.
- Sudo adapter: failed; sudo commands can validate and dry-run without approval.
- Docker adapter: failed; `docker system prune -af` can validate and dry-run when allowlisted.
- Systemctl adapter: partially passed; service/action allowlist exists, but CLI dry-run fixture currently fails before adapter execution.
- Executor integration: partially passed; real metadata bypass is improved, but CLI request loading is broken for metadata command_ref and some adapter policy checks are still insufficient.
- CLI:
  - `adapter status`: partially passed; command runs but omits required safety fields.
  - `adapter validate-policy`: partially passed; command runs but validation remains superficial.
  - `adapter dry-run`: failed; required fixture path errors before artifact generation.

## Validation Results

- Targeted R5 tests: passed, 30 passed.
- R4 regression tests: passed, 45 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 572 passed.
- `make validate-examples`: passed.
- `agentcomos healthcheck`: passed via `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli healthcheck`.
- `agentcomos discord status`: passed/unavailable as expected; token missing and disabled.
- `agentcomos executor status`: passed; default disabled, dry-run-only true, real execution unavailable.
- `agentcomos adapter status`: command runs; field completeness failed.
- `agentcomos adapter dry-run`: failed with duplicate `command_ref` constructor argument error.
- `docker compose config`: passed with Docker's existing obsolete `version` warning; no docker.sock/privileged/host-root/ssh-key mount found.
- `docker build/run`: passed; image built and `agentcomos healthcheck`, `agentcomos executor status`, and `agentcomos adapter status` ran successfully.

## Hygiene And Security

- Forbidden diff scan: passed; no `.agentcomos/runs`, `.env`, `uv.lock`, R6/R7/G12 files in the R5 diff.
- Local ignored files: `.env` exists in the local workspace and was not modified or staged by Codex.
- Compose boundary scan: passed; no docker.sock mount, privileged container, host root mount, ssh key mount, systemd mount, or cgroup mount found.
- Source secret scan: no real private keys or committed production tokens found. Placeholder and fake test redaction strings were observed and treated as non-secret fixtures.

## Required Fixes Before Re-review

- Fix `ExecutorRequest.from_dict()` / metadata handling so request fixtures with `metadata.command_ref` load exactly once and `agentcomos adapter dry-run` writes artifacts.
- Block `docker system prune`, privileged docker run, docker exec shell, and other destructive docker templates even when command_ref is allowlisted.
- Require approval for sudo operations and block bare/raw sudo templates.
- Apply rendered-command safety validation to SSH commands, not only shell commands.
- Update `adapter status` to report `enabled: false` and `real_execution_available: false` per adapter.
- Replace placeholder blocker tests with assertions for the CLI dry-run fixture, docker destructive blocking, sudo approval blocking, SSH dangerous command blocking, Discord non-bypass, compose boundary, and artifact secret checks.

### Antigravity follow-up fix
**Status:** ready for Codex re-review

**Fixed:**
* adapter dry-run no longer crashes on existing fixtures with duplicate command_ref.
* Command_ref canonicalization now prevents duplicate constructor arguments.
* Docker destructive commands such as docker system prune -af are blocked even if allowlisted.
* Sudo commands require approval even if allowlisted.
* SSH rendered commands are scanned after rendering; rendered rm -rf / is blocked.
* Adapter status now reports dry-run/mock capability.
* R5 blocker tests now contain real assertions for all previous blocker paths.
* Exact Codex reproductions pass.
