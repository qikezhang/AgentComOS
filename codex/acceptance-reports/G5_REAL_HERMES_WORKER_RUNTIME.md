# G5 — Real Hermes Worker Runtime Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

passed

## Scope

Unlocked after fake tmux worker E2E passes. This review covers G5 Real Hermes Worker Runtime only. G6 Evidence / Delivery / GM Report is not unlocked until this G5 report is passed and merged.

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

- Audit time: `2026-06-09 00:14:26 CST +0800` / `2026-06-08T16:14:26Z`
- Auditor: Codex
- Branch reviewed: `antigravity/g5-real-hermes-worker-runtime`
- Commit reviewed: `b2984d0f9749436f0bf56c723eaff6adeb2bbbca`
- Host facts probed: global `agentcomos` not on PATH; `.venv/bin/agentcomos` available; `hermes` not on PATH; `tmux` not on PATH; `opencode` not on PATH.

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g5-real-hermes-worker-runtime
git pull origin antigravity/g5-real-hermes-worker-runtime
git status
git log --oneline -15
git diff --name-status origin/main...HEAD
git status --short
make compile
make test
make validate-examples
grep -R "status_routes_to_real_handler\|unavailable.*status" tests || true
grep -R "collect_routes_to_real_handler\|unavailable.*collect" tests || true
grep -R "without_done\|DONE.md" tests/test_worker_g5* tests || true
grep -R "real_hermes_used.*routing\|not_routing_field" tests || true
grep -R "fake.*routes\|fake_worker.*handler" tests || true
grep -R "unknown.*runtime.*fail" tests || true
grep -R "does_not_start_loop_manual_evolution\|Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner" tests || true
./.venv/bin/agentcomos worker hermes-status || true
find .agentcomos -name "*hermes*status*.yaml" -print
find .agentcomos -name "*worker_runtime_status*.yaml" -print
rm -rf .agentcomos/runs/OI-TECHAI8-001
./.venv/bin/agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
./.venv/bin/agentcomos worker start --invocation examples/techai8/run/OI-TECHAI8-001/worker_invocations/HWI-TF-001.yaml --real || true
./.venv/bin/agentcomos worker status --job HWJ-OI-TECHAI8-001-TF-001-001 || true
./.venv/bin/agentcomos worker collect --job HWJ-OI-TECHAI8-001-TF-001-001 || true
./.venv/bin/agentcomos worker recover --run OI-TECHAI8-001 || true
rm -rf .agentcomos/runs/OI-TECHAI8-001
./.venv/bin/agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
./.venv/bin/agentcomos worker start --invocation examples/techai8/run/OI-TECHAI8-001/worker_invocations/HWI-TF-001.yaml --fake || true
./.venv/bin/agentcomos worker status --job HWJ-OI-TECHAI8-001-TF-001-001 || true
./.venv/bin/agentcomos worker collect --job HWJ-OI-TECHAI8-001-TF-001-001 || true
grep -R "Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor" src tests scripts || true
find .agentcomos/runs -path "*loops*" -o -path "*manual_updates*" -o -path "*worker_evolution*" -o -path "*auto_versioner*" -o -path "*decision_market*" -o -path "*feynman*" 2>/dev/null || true
grep -R "hermes chat\|hermes" src tests scripts || true
grep -R "tmux new-session\|tmux send-keys\|tmux has-session\|tmux attach" src tests scripts || true
```

G1/G2/G3/G4 regression commands were also executed with the repository CLI at `./.venv/bin/agentcomos` because the global command is not installed on this host.

## Verification Results

- `make compile`: passed.
- `make test`: passed, `144 passed in 2.49s`.
- `make validate-examples`: passed.
- Hermes status command: passed through `./.venv/bin/agentcomos worker hermes-status`; no crash.
- Hermes availability: unavailable on this host, correctly reported as `available: false`, `reason: hermes not found`, `version: unknown`, `runtime: real_hermes`.
- Hermes runtime status artifact: generated at `.agentcomos/worker-runtime/hermes_runtime_status.yaml` with `runtime`, `available`, `checked_at`, `reason`, and `version`; removed during cleanup as runtime-generated state.
- Real unavailable job YAML: passed. The generated job used `runtime: real_hermes`, `attempted_real_hermes: true`, `real_hermes_used: false`, `fake_worker: false`, `status: unavailable`, `failure_reason: hermes not found`, `tmux_used: false`, and an attempted `hermes chat -Q -q --invocation` command. It was not marked completed.
- Real unavailable status route: passed. `worker status` printed the real Hermes job and did not enter fake `DONE.md` collection behavior.
- Real unavailable collect route: passed. `worker collect` returned `Cannot collect unavailable worker job ... hermes not found`, did not mention fake `DONE.md`, did not create fake outputs, and did not mark the job completed.
- Collect does not require fake `DONE.md`: passed by manual CLI verification and explicit G5 test coverage.
- `real_hermes_used` is not a routing field: passed. Tests prove `runtime: real_hermes` / `attempted_real_hermes: true` route real, while `real_hermes_used` alone routes `unknown`.
- Fake worker runtime preserved: passed. On this host without tmux, fake start records `runtime: tmux_fake_hermes`, `fake_worker: true`, `real_hermes_used: false`, `status: unavailable`, and `failure_reason: tmux not found on PATH`; it is not routed to the real handler.
- Fake worker output contract verified without real tmux: passed through automated tests that directly exercise fake output writing and assert `DONE.md`, `result.yaml`, and `reasoning_summary.md`.
- No Loop / Manual / Worker Evolution / Auto Versioner: passed. G5 runtime did not create those run directories, and worker source boundary grep did not find those runtime implementations. Test `test_real_hermes_does_not_start_loop_manual_evolution` now has concrete assertions.
- G1 regression: passed. `run create`, `run status`, `controller tick --fake`, and `controller recover` succeeded.
- G2 regression: passed. Fake OpenCode submit/status/collect succeeded and stayed `runtime: fake_opencode`.
- G3 regression: passed. Real OpenCode status safely reported `available: false`, `reason: opencode not found`.
- G4 regression: passed. Fake worker path safely returned tmux unavailable on this host and preserved fake runtime identity.
- Boundary check: passed. Real Hermes command construction is limited to explicit real worker path; fake path command builder uses `scripts/fake_hermes_worker.py` and does not call real Hermes. `make test` passed without real Hermes or real tmux.
- Runtime artifacts cleanup: passed. Generated `.agentcomos/worker-runtime/hermes_runtime_status.yaml` and generated run artifacts were removed; tracked historical `.agentcomos/runs` fixture files were restored to avoid committing operating-data changes.
- `uv.lock` not committed: passed. An untracked `uv.lock` existed before audit and was not staged or committed.

## Test Coverage Confirmed

- `test_real_hermes_unavailable_job_status_routes_to_real_handler`
- `test_real_hermes_unavailable_job_collect_routes_to_real_handler_without_done_md`
- `test_real_hermes_job_routes_by_runtime_even_when_real_hermes_used_false`
- `test_attempted_real_hermes_routes_to_real_handler`
- `test_real_hermes_used_is_not_routing_field`
- `test_fake_worker_still_routes_to_fake_handler`
- `test_unknown_worker_runtime_fails_safely`
- `test_real_hermes_does_not_start_loop_manual_evolution`
- `test_fake_hermes_worker_output_contract_without_tmux`
- `test_fake_hermes_worker_writes_done_result_summary_without_real_hermes`
- `test_g4_fake_worker_output_contract_preserved_after_g5`

The previously blocking empty/pass-only Loop/Manual/Evolution test is no longer a placeholder.

## Findings

- No blocking issues remain.
- Branch scope is acceptable for G5: real Hermes availability, real worker runtime, worker routing, CLI worker commands, G5 tests, task/report documentation, and necessary G4 regression tests.
- The current host cannot manually observe a tmux-backed fake worker completion because `tmux` is not installed, but the required safety behavior is correct and the fake output contract is covered by tests without real tmux.

## Rollback Note

Roll back G5 by removing the real Hermes worker runtime module, real worker CLI path, Hermes availability artifact writer, G5 tests, and G5 docs/report changes. Preserve G4 fake Hermes worker runtime and do not rewrite `.agentcomos/runs` operating data history.

## Decision

G5 passed.

G6 Evidence / Delivery / GM Report may start after merge.

## Next Gate Unlock Status

Unlocked after this G5 branch is merged. Antigravity may start G6 Evidence / Delivery / GM Report from latest main after merge.
