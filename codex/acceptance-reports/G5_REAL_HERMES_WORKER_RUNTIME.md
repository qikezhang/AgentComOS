# G5 — Real Hermes Worker Runtime Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

failed

## Scope

Unlocked after fake tmux worker E2E passes.

## Inputs Reviewed

- `AGENTS.md`
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/modules/03_hermes_tmux_worker_pool.md`
- `docs/runbooks/tmux-worker-pool.md`
- `docs/27_RUNTIME_JOB_ROUTING_RULES.md`
- `antigravity/tasks/phase-5-real-hermes-worker-runtime.md`
- `codex/acceptance-reports/G5_REAL_HERMES_WORKER_RUNTIME.md`

## Audit Metadata

- Audited at: 2026-06-08T15:39:35Z
- Auditor: Codex
- Branch: `antigravity/g5-real-hermes-worker-runtime`
- Commit reviewed: `870d25ed036afa064c0e8f0ae3671df72dbb3ef3`
- Host facts probed: global `agentcomos` not on PATH; `.venv/bin/agentcomos` available; `hermes` not on PATH; `tmux` not on PATH; `opencode` not on PATH.

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g5-real-hermes-worker-runtime
git pull --ff-only origin antigravity/g5-real-hermes-worker-runtime
git status --short
git log --oneline -12
git diff --name-status origin/main...HEAD
grep -R "Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor" src tests scripts docs antigravity codex || true
grep -R "hermes chat\|hermes" src tests scripts || true
grep -R "tmux new-session\|tmux send-keys\|tmux has-session\|tmux attach" src tests scripts || true
make compile
make test
make validate-examples
./.venv/bin/agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
./.venv/bin/agentcomos run status --run OI-TECHAI8-001
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller recover --run OI-TECHAI8-001
./.venv/bin/agentcomos opencode submit --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos opencode status --job OCJ-OI-TECHAI8-001-001
./.venv/bin/agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001
./.venv/bin/agentcomos opencode status
./.venv/bin/agentcomos worker start --invocation examples/techai8/run/OI-TECHAI8-001/worker_invocations/HWI-TF-001.yaml --fake
./.venv/bin/agentcomos worker status --job HWJ-OI-TECHAI8-001-TF-001-001
./.venv/bin/agentcomos worker collect --job HWJ-OI-TECHAI8-001-TF-001-001
./.venv/bin/agentcomos worker hermes-status
./.venv/bin/agentcomos worker start --invocation examples/techai8/run/OI-TECHAI8-001/worker_invocations/HWI-TF-001.yaml --real
./.venv/bin/agentcomos worker status --job HWJ-OI-TECHAI8-001-TF-001-001
./.venv/bin/agentcomos worker collect --job HWJ-OI-TECHAI8-001-TF-001-001
./.venv/bin/agentcomos worker recover --run OI-TECHAI8-001
./.venv/bin/agentcomos worker start --invocation /tmp/not-exist-worker-invocation.yaml --real
./.venv/bin/agentcomos worker status --job HWJ-REAL-DOES-NOT-EXIST
./.venv/bin/agentcomos worker collect --job HWJ-REAL-DOES-NOT-EXIST
```

Results:

- `make compile`: passed.
- `make test`: passed, 135 tests.
- `make validate-examples`: passed.
- G1 Controller regression: passed.
- G2 fake OpenCode regression: passed.
- G3 real OpenCode availability regression: passed; reported `available: False`, `reason: opencode not found`.
- G4 fake Hermes worker regression: host has no `tmux`; start recorded `runtime: tmux_fake_hermes`, `status: unavailable`, `real_hermes_used: false`, and collect failed cleanly. Full `DONE.md` / `result.yaml` / `reasoning_summary.md` generation was not manually verifiable on this host.
- G5 real Hermes unavailable path: passed safety behavior; start recorded `runtime: real_hermes`, `attempted_real_hermes: true`, `fake_worker: false`, `real_hermes_used: false`, `status: unavailable`, `failure_reason: hermes not found`, and `attempted_command` containing `hermes chat -Q -q`.
- G5 real Hermes status/collect/recover: status routed to the real job and showed unavailable; collect failed cleanly without requiring fake `DONE.md`; recover preserved `runtime: real_hermes` and `status: unavailable`.
- Negative checks: missing run, missing invocation, missing job status, and missing job collect all failed cleanly.

## Required Artifacts Checked

- Real unavailable worker job YAML was generated and checked at `.agentcomos/runs/OI-TECHAI8-001/worker_jobs/HWJ-OI-TECHAI8-001-TF-001-001.yaml`.
- The real unavailable job included `job_id`, `run_id`, `task_id`, `runtime: real_hermes`, `attempted_real_hermes: true`, `created_by: controller`, `started_by: controller`, `real_hermes_used: false`, `fake_worker: false`, logs, `attempted_command`, and `failure_reason`.
- No Hermes runtime status YAML artifact was found.
- No `.agentcomos/runs` runtime artifact changes were left in the working tree after cleanup.

## Positive Tests

- `test_real_hermes_submit_requires_existing_run`
- `test_real_hermes_status_handles_missing_binary`
- `test_real_hermes_missing_binary_creates_blocked_or_unavailable_job`
- `test_real_hermes_unavailable_job_has_failure_reason`
- `test_real_hermes_does_not_fake_completion`
- `test_real_hermes_job_routes_by_runtime_not_real_hermes_used`
- `test_fake_hermes_runtime_still_passes_after_g5`
- `test_make_tests_do_not_require_real_hermes`
- `test_real_hermes_does_not_start_loop_manual_evolution`
- `test_no_agentcomos_runs_artifacts_committed`

## Negative Tests

- Missing run real worker start failed with no orphan worker job.
- Missing invocation real worker start failed.
- Missing job status failed.
- Missing job collect failed.
- Unknown runtime, real unavailable status routing, real unavailable collect routing, and collect-unavailable-without-DONE.md are not covered by explicit G5 tests.

## Evidence Artifacts

- `make compile` output: passed.
- `make test` output: 135 passed.
- `make validate-examples` output: passed.
- Real unavailable job sample was generated during audit and removed from the working tree after inspection.

## Antigravity Implementation Report

- Implementation completed by Antigravity.
- Real Hermes uses `tmux` and `hermes chat -Q -q --invocation <file>`.
- Properly handles missing binary (records `unavailable` or `blocked` status with `hermes not found` without failing ungracefully).
- Strictly maintains `attempted_real_hermes` and uses `detect_job_runtime` for proper routing. Fake workers remain untampered.
- CLI handles `--fake` and `--real` flags strictly.

## Codex Findings

- Branch scope is acceptable: changes are limited to G5 worker runtime, CLI, G5 tests, G5 task/report docs, and necessary G4 test updates.
- Boundary search did not find Loop Execution, Manual OS, Worker Evolution, Auto Versioner, Decision Market executor, or Feynman executor implementation in the G5 runtime path. Matches were existing specification, roadmap, task, and acceptance-report text.
- Real Hermes command construction is controlled by the explicit `--real` path and uses `tmux` plus `hermes chat -Q -q --invocation`.
- Fake Hermes runtime remains routed as `tmux_fake_hermes`; on this host without `tmux`, it fails safely as unavailable rather than pretending completion.
- Real unavailable jobs route by `runtime: real_hermes` / `attempted_real_hermes: true`, not by `real_hermes_used`.
- `worker hermes-status` is missing, and no equivalent worker-scoped Hermes availability command or runtime status artifact with `runtime`, `available`, `checked_at`, `reason`, and `version` was found.
- Required G5 routing and negative coverage is incomplete.

## Blocking Issues

1. Missing required Hermes availability command/artifact.
   - `agentcomos worker hermes-status` fails with "No such command 'hermes-status'".
   - No equivalent worker availability command was identified.
   - No Hermes runtime status YAML artifact was generated or found.
   - Acceptance requires clear `available: false` / unavailable, `reason`, `checked_at`, and `version` without crashing.

2. Required G5 test coverage is incomplete.
   - No explicit G5 test proves unknown worker runtime fails safely and does not default to fake.
   - No explicit G5 CLI/status test proves unavailable real Hermes jobs route to the real status handler.
   - No explicit G5 CLI/collect test proves unavailable real Hermes jobs route to the real collect handler.
   - No explicit test proves real unavailable collect does not require fake `DONE.md`.
   - `test_real_hermes_does_not_start_loop_manual_evolution` is a `pass` placeholder rather than a meaningful regression.

## Non-blocking Issues

- The G5 tests monkeypatch `agentcomos.worker.availability.check_hermes_availability`, but `real_runtime.py` imports `check_hermes_availability` directly. On hosts with `hermes` installed, those monkeypatches may not control the code under test.
- The host lacks `tmux`, so the manual G4 fake worker output-generation regression could not be fully observed. The unavailable safety behavior was correct, and the automated G4/G5 tests passed.
- Real worker job YAML uses nested `logs.stdout` / `logs.stderr` rather than top-level `stdout_log` / `stderr_log`; this is probably equivalent, but the field naming should be confirmed in the contract.

## Rollback Note

- Roll back G5 by removing the real Hermes worker runtime module, real worker CLI path, G5 tests, and G5 docs/report changes. Preserve G4 fake Hermes worker runtime and do not rewrite `.agentcomos/runs` operating data history.

## Decision

G5 failed. Antigravity must fix the blocking issues in the G5 branch before G6 Evidence / Delivery / GM Report may start.

## Next Gate Unlock Status

Locked. G6 must not start until this report is marked `passed`.
