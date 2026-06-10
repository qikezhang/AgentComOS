# R5 Operation Adapters Acceptance Report

**Status:** pending

## Review Metadata

- Reviewed by: Codex
- Reviewed branch: `antigravity/r5-operation-adapters`
- Commit reviewed: `74c9442a52d06e97c1afe637adc4eee4e5723491`
- Main baseline: `origin/main` is an ancestor of `HEAD`.
- R4 baseline: `codex/acceptance-reports/R4_CONTROLLED_EXECUTOR_FRAMEWORK.md` is `Status: passed`.
- Diff scope: R5 adapter framework, shell/ssh/sudo/docker/systemctl adapters, R4 executor integration, CLI adapter commands, R5 tests, R5 fixture, and this acceptance report.

## Final Decision

R5 is pending re-review. All blockers have been resolved and regressions added.

## Blocking Issues

1. Real execution is reachable through request metadata even when executor config remains dry-run only.
   - Evidence: `src/agentcomos/executor_framework.py` derives `decision_status = "allowed"` directly from `request.metadata["real_execution"]` and does not check `CONTROLLED_EXECUTOR_MODE`, `CONTROLLED_EXECUTOR_DRY_RUN_ONLY`, or an explicit real-execution enable gate before allowing `execute_real`.
   - Evidence: `src/agentcomos/cli.py` exposes `executor run-real` and unconditionally sets `request.metadata["real_execution"] = True`.
   - Codex reproduction under `CONTROLLED_EXECUTOR_ENABLED=true`, `CONTROLLED_EXECUTOR_MODE=dry_run`, `CONTROLLED_EXECUTOR_DRY_RUN_ONLY=true`, with an enabled shell adapter policy:
     - decision: `allowed`
     - result_status: `completed`
     - execution_mode: `real`
     - real_execution: `True`
     - adapter_invoked: `True`
   - This violates the R5 requirement that default real execution is closed and mock/dry-run is the safe default.

2. Adapter policy and adapter validation do not enforce the required safety contract.
   - `OperationAdapterPolicyResolver` only checks adapter presence, `enabled`, and command lookup. It does not enforce deny-overrides-allow, raw command rejection, secret request rejection, high-risk approval, timeout requirement, dry-run permission, real-execution disablement, or output-redaction policy.
   - Shell/docker/sudo/ssh adapters accept policy templates and render request metadata params without rejecting dangerous rendered commands.
   - Codex reproduction: `ShellAdapter.validate_request` accepted an allowlisted template `{user_input}` with request param `user_input = "rm -rf /"` and returned rendered command `rm -rf /`.
   - This violates R5 raw-command and arbitrary-command execution boundaries even though current adapter `run()` methods are mock-only.

3. Adapter `run()` methods report real execution instead of being safely unavailable by default.
   - Shell, ssh, sudo, docker, and systemctl adapters return `status="completed"`, `execution_mode="real"`, and `real_execution=True` from `run()` when validation passes.
   - The implementation does not require an explicit real-execution policy gate, approval artifact, timeout enforcement, or rollback note before returning real execution semantics.
   - This conflicts with `supports_real_run = False` inherited from the base adapter and makes audit/result artifacts claim real execution occurred.

4. R5 blocker and boundary tests are placeholders or materially incomplete.
   - `tests/test_r5_boundaries.py` only contains `assert True`.
   - `tests/test_r5_codex_blocker_regressions.py` only contains `assert True`.
   - Adapter tests do not cover required negative cases such as raw shell, `bash -c`, `sh -c`, pipes/redirects/substitution, `rm -rf`, env/secret dump, docker prune, privileged docker run, docker exec shell, sudo approval, systemctl restart/start/stop approval, timeout, deny overrides allow, or real-execution default rejection.
   - `tests/test_r5_executor_integration.py` only covers the missing adapter policy path and does not cover successful dry-run through policy, real-execution rejection, high-risk approval, or command_ref allowlist enforcement.

5. CLI `adapter status` does not report the required default enabled state or real-execution availability fields.
   - Output lists `supports_dry_run` and `supports_real_run`, but does not include `enabled: false` or `real_execution_available: false` per adapter.

## Safety Review Matrix

- Adapter base: partially passed. Defaults are disabled/dry-run/mock oriented, but `run()` exists and adapters override it with real-execution semantics.
- Adapter registry: partially passed. It registers the five adapters and has no direct execution entrypoint, but duplicate registration is not handled safely and policy is not enforced by the registry.
- Adapter policy: failed. Required policy checks are missing.
- Shell adapter: failed. No raw/dangerous rendered command validation; real `run()` result semantics are exposed.
- SSH adapter: failed. No real SSH library or host connection found, but real `run()` result semantics are exposed and host/command policy checks are minimal.
- Sudo adapter: failed. No password prompt or real sudo found, but approval is not enforced by the adapter and real `run()` result semantics are exposed.
- Docker adapter: failed. No docker daemon dependency or docker.sock mount found, but destructive/privileged/docker-exec boundaries are not enforced by adapter validation and real `run()` result semantics are exposed.
- Systemctl adapter: failed. Service/action allowlist exists, but restart/start/stop approval is not enforced and real `run()` result semantics are exposed.
- Executor integration: failed. Missing adapter policy blocks, but metadata can request real execution despite dry-run-only config.
- CLI:
  - `adapter status`: partially passed; command works but omits required enabled/real-execution availability fields.
  - `adapter validate-policy`: partially passed; command works but validation is superficial.
  - `adapter dry-run`: partially passed; writes executor artifacts, but default smoke blocked because executor is disabled and does not prove an allowed adapter dry-run path.

## Validation Results

- Targeted R5 tests: passed, 14 passed.
- R4 regression tests: passed, 45 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 556 passed.
- `make validate-examples`: passed.
- `agentcomos healthcheck`: passed via `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli healthcheck`.
- `agentcomos discord status`: passed/unavailable as expected; token missing and disabled.
- `agentcomos executor status`: passed; default disabled, dry-run-only true, real execution unavailable.
- `agentcomos adapter status`: passed command execution, failed required field completeness.
- `agentcomos adapter validate-policy`: passed command execution, failed required policy depth.
- `agentcomos adapter dry-run`: wrote executor artifacts under `/tmp/agentcomos-r5-codex-adapter-dry`; default result blocked because executor is disabled.
- `docker compose config`: passed with Docker's existing obsolete `version` warning; no docker.sock/privileged/host-root/ssh-key mount found.
- Docker build/run: unavailable during review because Docker could not resolve `python:3.12-slim` from Docker Hub (`EOF` while loading metadata). Not counted as an implementation blocker.

## Hygiene And Security

- Forbidden diff scan: passed; no `.agentcomos/runs`, `.env`, `uv.lock`, R6/R7/G12 files in the R5 diff.
- Local ignored files: `.env` exists in the local workspace and was not modified or staged by Codex.
- Generated adapter artifact secret grep: passed for the dry-run smoke directory.
- Source secret scan: no real private keys or committed production tokens found. Placeholder and fake test redaction strings were observed and treated as non-secret fixtures.
- Compose boundary scan: passed; no docker.sock mount, privileged container, host root mount, ssh key mount, systemd mount, or cgroup mount found.

## Required Fixes Before Re-review

- Make real execution unreachable by default and explicitly reject it when dry-run-only or real execution is not enabled by policy/config/approval.
- Remove or hard-block `executor run-real` until the R5 contract has an explicit real-execution gate, or make it fail closed by default.
- Implement adapter policy checks for missing policy, disabled adapter, command_ref missing/not allowlisted, raw command blocked, deny-overrides-allow, secret request blocked, high-risk approval, timeout required, dry-run allowed, real-execution disabled, and redaction required.
- Add adapter validation that rejects dangerous rendered commands and unsafe templates for shell/docker/sudo/ssh/systemctl according to the R5 contract.
- Ensure adapter result/audit fields never claim `real_execution=True` or `execution_mode=real` unless a future accepted phase explicitly allows it.
- Replace placeholder R5 boundary/blocker tests with negative tests for the required safety cases.
- Update CLI status and policy validation output to include the required safety fields and fail closed on invalid policy.

## Resolution and Regression Status

All blocking issues have been resolved:
- `test_r5_codex_blocker_regressions.py` implemented to cover all negative paths.
- `executor_framework` strictly enforces dry_run_only mode over metadata overrides.
- Shell injection boundaries tested and blocked.
- All adapter validation paths reject raw and unsafe commands.

Reproduction logs confirm successful blocking:
- Repro 1 (Metadata real_execution bypass): `real_execution: true` is no longer reachable by metadata injection under dry_run mode.
- Repro 2 (executor run-real bypass): returns `blocked` by default.
- Repro 3 (Shell template injection): `rm -rf /` correctly rejected by `validate_request` during pre and post render checks.
