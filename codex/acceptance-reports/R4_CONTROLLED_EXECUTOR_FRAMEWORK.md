# R4 Controlled Executor Framework - Acceptance Report

**Status:** failed

## Codex Review

- Reviewed branch: `antigravity/r4-controlled-executor-framework`
- Reviewed commit: `9363846 feat(executor): implement R4 controlled executor framework`
- Review date: 2026-06-11 Asia/Shanghai

## Codex Re-review 2

- Reviewed branch: `antigravity/r4-controlled-executor-framework`
- Reviewed commit: `f07e2dc fix(r4): redact secret data from executor artifacts and CLI`
- Review date: 2026-06-11 Asia/Shanghai
- Previous blocker status: fixed; disabled and missing-policy secret requests no longer persist raw `token=xxx` text in generated artifacts.

### Blocking Issues

1. Secret request semantics regress after early redaction.
   - Reproduction:
     - Create a policy with `allowed_sources: [discord]`.
     - Run `CONTROLLED_EXECUTOR_ENABLED=true CONTROLLED_EXECUTOR_POLICY_PATH=/tmp/agentcomos-r4-codex-policy-smoke/policy.yaml PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli executor run-dry --request-file tests/fixtures/executor/blocked_secret_request.yaml --runtime-dir /tmp/agentcomos-r4-codex-policy-smoke/secret`
   - Observed decision artifact:
     - `decision: blocked`
     - `reason: command_unknown`
     - `risk_level: unknown`
   - Expected:
     - `reason: secret_request_blocked`
     - `risk_level: secret`
   - Root cause from review: `ExecutorRequest.from_dict()` / construction redacts `token=xxx` before `ExecutorClassifier.classify_command()` runs, so the classifier no longer sees the token pattern and downgrades the request to unknown. R4 requires token/secret/private-key requests to remain explicitly blocked as secret requests, not harmless unknowns.

### Re-review Validation Evidence

- Diff scope from `88a3d47..f07e2dc`: redaction helper, request/decision/result/audit/CLI redaction wiring, R4 redaction tests, and report notes only.
- Forbidden file scan: passed; no `.agentcomos/runs`, `.env`, `uv.lock`, G12 files, or operation adapter implementations in the diff.
- R5 boundary: passed; no shell/ssh/sudo/docker/systemctl adapter implementation, no `subprocess`/`os.system` path in R4 executor code, no `paramiko`, no docker.sock, no privileged container.
- Previous artifact leak reproduction:
  - disabled executor path: passed; no raw `token=xxx` persisted.
  - missing-policy path: passed; no raw `token=xxx` persisted.
- Enabled policy smoke:
  - read-only status: `allowed_dry_run`, `real_execution: false`, `adapter_invoked: false`.
  - restart service: `requires_approval`, `real_execution: false`, `adapter_invoked: false`.
  - shell command: `blocked`, `reason: direct_system_command_blocked`.
  - secret request: failed; blocked as `command_unknown` instead of `secret_request_blocked`.
- Targeted R4 tests: passed, 35 passed.
- R3 regression tests: passed, 72 passed.
- R2 regression tests: passed, 11 passed.
- `make compile`: passed.
- `make test`: passed, 532 passed.
- `make validate-examples`: passed.
- `agentcomos healthcheck`: passed.
- `agentcomos discord status`: passed/unavailable as expected.
- `agentcomos discord serve`: passed/unavailable as expected.
- `agentcomos executor status`: passed.
- `agentcomos executor evaluate`: passed.
- `agentcomos executor run-dry`: functionally dry-run only, but failed acceptance because secret request reason semantics regressed.
- `docker compose config`: passed with Docker's existing obsolete `version` warning.
- `docker build/run`: unavailable; Docker Hub `python:3.12-slim` metadata fetch failed with EOF.
- Generated artifact secret scan: passed for raw token/private-key patterns.

### Re-review Final Decision

R4 is still not accepted. Antigravity must preserve secret classification semantics while keeping artifacts redacted. R5 remains locked.

## Blocking Issues

1. Secret-bearing requests are persisted before redaction on disabled and missing-policy deny paths.
   - Reproduction:
     - `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli executor run-dry --request-file tests/fixtures/executor/blocked_secret_request.yaml --runtime-dir /tmp/agentcomos-r4-codex-secret-disabled`
     - `CONTROLLED_EXECUTOR_ENABLED=true PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli executor run-dry --request-file tests/fixtures/executor/blocked_secret_request.yaml --runtime-dir /tmp/agentcomos-r4-codex-secret-missing`
   - Observed artifacts:
     - `/tmp/agentcomos-r4-codex-secret-disabled/executor_request_EXEC-REQ-31865A28.yaml`
     - `/tmp/agentcomos-r4-codex-secret-disabled/executor_audit.yaml`
     - `/tmp/agentcomos-r4-codex-secret-missing/executor_request_EXEC-REQ-31865A28.yaml`
     - `/tmp/agentcomos-r4-codex-secret-missing/executor_audit.yaml`
   - These artifacts contain `command_text_redacted: show secret token=xxx`.
   - This violates the R4 acceptance requirements that secret requests are blocked without persisting token/secret material, that command text is redacted in artifacts, and that missing-policy/default-deny paths remain safe.

## Validation Evidence

- Branch baseline: passed; `origin/main` is an ancestor of `HEAD`.
- R3 acceptance report baseline: passed; `codex/acceptance-reports/R3_REAL_DISCORD_BOT_ADAPTER.md` is `Status: passed`.
- Initial R4 report state: passed; Antigravity submitted this report as `PENDING`, with no forged Codex approval.
- Diff scope: mostly R4 executor framework, tests, fixtures, CLI, Discord integration, and `.env.example`; no R5 adapter files were added.
- Forbidden file scan: passed; no `.agentcomos/runs`, `.env`, `uv.lock`, G12 files, or operation adapter implementations in the diff.
- Executor config: passed; defaults are disabled, default deny, high-risk approval required, and dry-run only.
- Request model: partially passed; required fields are present, but blocked by the redaction persistence issue above.
- Command classifier: passed; secret, direct system, destructive, unknown, read-only, and restart classifications are covered.
- Policy evaluation: partially passed; disabled and missing policy deny, secret/direct/destructive classifications block, and high-risk requests require approval. The blocking redaction issue prevents acceptance.
- Decision artifact: generated.
- Result artifact: generated with `execution_mode: dry_run`, `real_execution: false`, and `adapter_invoked: false`.
- Audit artifact: generated, but blocked because disabled and missing-policy secret paths persist unredacted token text.
- Dry-run mode: passed; no real execution path found in R4 executor code.
- CLI smoke:
  - `executor status`: passed; reports `real_execution_available: false` and `adapters_available: false`.
  - `executor evaluate`: passed; writes request and decision artifacts.
  - `executor run-dry`: functionally runs dry, but failed acceptance because secret-bearing disabled/missing-policy paths leak token text to artifacts.
- R3 GM command integration: passed for dry-run-only boundary; Discord generates executor request artifacts and does not directly execute system commands.
- Safety:
  - default deny: passed.
  - missing policy deny: passed for decision, failed for redaction hygiene.
  - secret request blocked: passed for decision, failed for artifact redaction.
  - direct system command blocked: passed.
  - high risk requires approval: passed.
  - real execution available: false.
  - operation adapters implemented: false.
  - subprocess/os.system used in R4 executor code: false.
  - docker.sock mounted: false.
  - privileged container: false.
- Validation:
  - targeted R4 tests: passed, 22 passed.
  - R3 regression tests: passed, 72 passed.
  - R2 regression tests: passed, 11 passed.
  - `make compile`: passed.
  - `make test`: passed, 519 passed.
  - `make validate-examples`: passed.
  - `agentcomos healthcheck`: passed.
  - `agentcomos discord status`: passed/unavailable as expected.
  - `agentcomos discord serve`: passed/unavailable as expected.
  - `agentcomos executor status`: passed.
  - `agentcomos executor evaluate`: passed.
  - `agentcomos executor run-dry`: failed acceptance due the blocker above.
  - `docker compose config`: passed with Docker's existing obsolete `version` warning.
  - `docker build/run`: unavailable; Docker Hub anonymous token fetch for `python:3.12-slim` failed with EOF, so image run checks were not completed.
- Hygiene:
  - `.agentcomos/runs` clean: passed.
  - `.env` not committed: passed; `.env.example` contains placeholders only.
  - `uv.lock` clean: passed.
  - secrets clean: failed for generated executor artifacts in the blocker reproduction.

## Final Decision

R4 is not accepted. Antigravity must fix the blocking redaction issue before R4 can be merged. R5 remains locked.

## Acceptance Criteria Checklist

### 1. Security Boundaries
- [x] No operation adapters exist (no `shell_adapter.py`, `sudo_adapter.py`, etc.).
- [x] R4 does not execute direct system commands (no subprocess, no os.system for payloads).
- [x] No credentials or `.env` secrets are read or handled by R4 logic.
- [x] Risk classification blocks unknown, destructive, and secret requests.

### 2. Required Models and Architecture
- [x] `ExecutorRequest` implemented and serialized.
- [x] `ExecutorDecision` implemented and serialized.
- [x] `ExecutorResult` implemented and serialized.
- [x] `ExecutorConfig` implemented using environment variables.
- [x] `ExecutorPolicy` implemented with YAML validation.

### 3. CLI Features
- [x] `agentcomos executor status` implemented.
- [x] `agentcomos executor evaluate` implemented (outputs request and decision).
- [x] `agentcomos executor run-dry` implemented (outputs request, decision, and result).

### 4. Integration with R3 (Discord Adapter)
- [x] Discord `ingest_test` generates an `ExecutorRequest` for commands requiring executor (`requires_executor=True` or `read_only`).
- [x] Source message ID and correlation ID are preserved.
- [x] R3 tests remain passing.

### 5. Testing
- [x] `tests/test_r4_executor_config.py` passes.
- [x] `tests/test_r4_executor_policy.py` passes.
- [x] `tests/test_r4_executor_classifier.py` passes.
- [x] `tests/test_r4_executor_decision.py` passes.
- [x] `tests/test_r4_executor_dry_run.py` passes.
- [x] `tests/test_r4_executor_artifacts.py` passes.
- [x] `tests/test_r4_executor_non_bypass.py` passes.
- [x] `tests/test_r4_executor_cli.py` passes.
- [x] `tests/test_r4_executor_boundaries.py` passes.
- [x] `tests/test_r4_codex_blocker_regressions.py` passes.

## Review Notes
The framework implements the strict request-decision-result architecture required by the Phase R4 specification. The executor defaults to `dry_run` mode and has no access to real adapters. It correctly interfaces with the Discord GM command artifacts and applies risk classifications. Real operation execution is deferred to Phase R5.

## Antigravity follow-up fix

Status: ready for Codex re-review

Fixed:
- Added executor-wide recursive redaction.
- Redacted request ingestion before artifact serialization.
- Redacted disabled executor deny path.
- Redacted missing policy deny path.
- Redacted secret request blocked path.
- Redacted run-dry result and audit.
- Added regression tests for generated artifact secret scan.
- Verified blocker reproduction no longer leaks raw secret text.

## Antigravity follow-up fix

Status: ready for Codex re-review

Fixed:
- Secret request classification now survives redaction.
- blocked_secret_request.yaml now produces risk_level: secret.
- blocked_secret_request.yaml now produces reason: secret_request_blocked.
- Secret request no longer falls back to command_unknown.
- Redaction still prevents raw token/password/api_key leakage.
- Classification uses raw semantic signal in memory.
- Artifacts/audit/CLI use redacted data only.
- Added regression tests for semantic-preserving redaction.
- Verified exact Codex reproduction.
