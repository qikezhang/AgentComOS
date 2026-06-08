# G2 — Fake OpenCode Runtime Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

failed

## Audit Metadata

- Audit time: 2026-06-08 16:19:22 CST (+0800)
- Auditor: Codex
- Branch reviewed: `antigravity/g2-fake-opencode-runtime`
- Commit reviewed: `73663c065ca115c019fdeb4c5d14c58f07cf970a`
- Working branch confirmed: `antigravity/g2-fake-opencode-runtime`

## Inputs Reviewed

- `AGENTS.md`
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/26_G1_TO_G2_HANDOFF.md`
- `docs/modules/02_opencode_runtime_manager.md`
- `antigravity/tasks/phase-2-fake-opencode-runtime.md`
- `codex/acceptance-reports/G2_FAKE_OPENCODE_RUNTIME.md`

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g2-fake-opencode-runtime
git pull origin antigravity/g2-fake-opencode-runtime
git status
git log --oneline -8
grep -R "opencode serve\|opencode run\|run --attach\|hermes chat\|tmux new-session\|tmux attach\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
make compile
make test
make validate-examples
```

## Validation Results

- `make compile`: passed.
- `make test`: passed, `73 passed in 1.46s`.
- `make validate-examples`: passed.
- Manual `run create`: passed for `OI-TECHAI8-001`.
- Manual fake controller ticks to `planning`: passed.
- Manual fake submit: passed for `OCJ-OI-TECHAI8-001-001`.
- Manual fake status: passed and reported `status: completed`, `runtime: fake_opencode`, `fake_runtime: true`, `real_opencode_used: false`, `real_hermes_used: false`.
- Manual fake collect: passed for `OCJ-OI-TECHAI8-001-001`.
- `run status`: passed.
- `controller recover`: passed.
- Controller fake tick integration: four fake ticks created exactly one fake OpenCode job and advanced to `executing`; additional ticks reached `completed` and generated delivery artifacts.

## Required Artifacts Checked

After the run was advanced to `completed`, the following artifacts existed:

- `.agentcomos/runs/OI-TECHAI8-001/opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_logs/OCJ-OI-TECHAI8-001-001.stdout.log`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_logs/OCJ-OI-TECHAI8-001-001.stderr.log`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_outputs/opencode_project_plan.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/delivery_packet.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/events.jsonl`
- `.agentcomos/runs/OI-TECHAI8-001/timeline.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/run_status.yaml`

Observation: immediately after the requested four-tick auto-scheduling sequence, `delivery_packet.yaml` was not yet present; it appeared only after additional ticks advanced the run to `delivery_ready` or later.

## Artifact Content Checks

- Job YAML minimum fields: present.
- Job ID: `OCJ-OI-TECHAI8-001-001`.
- Run ID: `OI-TECHAI8-001`.
- Runtime: `fake_opencode`.
- Job status: `completed`.
- `fake_runtime`: `true`.
- `real_opencode_used`: `false`.
- `real_hermes_used`: `false`.
- Job outputs include `opencode_outputs/opencode_project_plan.yaml` and `delivery_packet.yaml`.
- Job logs include stdout and stderr paths.
- Project plan minimum fields: present.
- Project plan `produced_by`: `fake_opencode`.
- Project plan `phase`: `plan`.
- Project plan constraints: `real_opencode_used: false`, `real_hermes_used: false`, `tmux_used: false`.
- Project plan tasks: at least one task present.
- Project plan next action: `Ready for Codex G2 review.`
- Delivery packet references `opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml` and `opencode_outputs/opencode_project_plan.yaml` after delivery generation.
- Events include `opencode.job.created`, `opencode.job.started`, `opencode.job.completed`, `opencode.output.generated`, and `delivery.updated`.
- Timeline includes G2 OpenCode job events after delivery generation.

## Idempotency Checks

- Repeated submit: passed for an existing completed job. No duplicate job was created, job count remained 1, and hashes for job, events, timeline, plan, stdout log, and stderr log were unchanged.
- Repeated collect: passed. Completed job state and artifact hashes were unchanged.
- Repeated status: passed. Status output was stable and read-only; hashes for job, events, timeline, plan, and logs were unchanged.
- Repeated controller tick after completion: passed for job idempotency and state stability. It did not create duplicate OpenCode jobs and did not roll back run state.

## Negative Tests

- `agentcomos opencode status --job OCJ-DOES-NOT-EXIST`: failed as expected with exit code 2.
- `agentcomos opencode collect --job OCJ-DOES-NOT-EXIST`: failed as expected with exit code 2.
- `agentcomos opencode submit --run OI-DOES-NOT-EXIST --fake`: failed acceptance. The command exited 0 and created an orphan run directory with job, logs, events, and output artifacts.
- Completed job without `delivery_packet.yaml`: failed acceptance. `collect` exited 0 even when `delivery_packet.yaml` was absent, contrary to `docs/18_ACCEPTANCE_GATES.md` negative test expectation.

## Test Coverage Review

Direct or equivalent coverage found:

- `test_fake_opencode_submit_generates_job`
- `test_fake_opencode_submit_generates_plan`
- `test_fake_opencode_submit_generates_logs`
- `test_fake_opencode_collect_reads_completed_job`
- `test_fake_opencode_status_reads_job`
- `test_fake_opencode_submit_is_idempotent`
- `test_controller_tick_fake_does_not_duplicate_opencode_job`
- `test_g2_delivery_packet_includes_opencode_outputs`
- `test_opencode_collect_missing_job_fails`
- `test_opencode_status_missing_job_fails`
- `test_cli_opencode_submit_real_fails` partially covers no real OpenCode via CLI behavior.

Missing or insufficient coverage:

- No direct equivalent for `test_g2_events_are_appended`.
- No direct equivalent for `test_no_real_opencode_or_hermes_usage` in the G2 tests.
- No direct equivalent for `test_opencode_submit_missing_run_fails`.
- No direct equivalent for `test_opencode_status_is_read_only`.
- No negative test for completed job missing `delivery_packet.yaml`.

## Boundary Check

No runtime execution of real OpenCode, real Hermes, tmux Worker Pool, Loop Execution, Manual OS, Worker Evolution, Auto Versioner, Decision Market executor, or Feynman executor was found in the G2 fake runtime path.

Grep hits were reviewed:

- `src/agentcomos/cli.py` contains inherited command skeleton printers for `tmux new-session`, `hermes chat -Q -q`, and `opencode run --attach`; these print commands and are not called by `opencode submit/status/collect --fake`.
- `.agentcomos/opencode-runtime/runtime_policy.yaml` contains `opencode serve` as policy/config text, not a G2 runtime invocation.
- Documentation and task files contain future-phase references to real OpenCode, Hermes, and tmux; classified as documentation-only/non-runtime.

Scope issues:

- The G2 branch includes changes outside the requested allowed G2 implementation surface: `codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md` was modified.
- The G2 branch deletes tracked `.agentcomos/runs/OI-TECHAI8-001/*` G1 run artifacts. Raw run data is not a release object, but this deletion is outside the user-provided G2 allowed range and should be resolved before acceptance.

Confirmations:

- Real OpenCode used: no.
- Real Hermes used: no.
- tmux Worker Pool implemented: no.
- Loop / Manual / Worker Evolution / Auto Versioner implemented: no.

## Blocking Issues

1. `agentcomos opencode submit --run OI-DOES-NOT-EXIST --fake` succeeds and creates an orphan fake OpenCode job under `.agentcomos/runs/OI-DOES-NOT-EXIST/`. G2 requires missing-run submit to fail and not create orphan artifacts.
2. `agentcomos opencode collect --job <completed_job>` succeeds when `delivery_packet.yaml` is missing. `docs/18_ACCEPTANCE_GATES.md` requires completed job without delivery packet to fail.
3. The G2 branch includes out-of-scope changes to `codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md` and deletion of tracked `.agentcomos/runs/OI-TECHAI8-001/*` artifacts, which are not in the requested G2 allowed range.

## Non-blocking Issues

- After the requested four fake controller ticks, `delivery_packet.yaml` is not yet generated; it appears only after additional ticks reach `delivery_ready` or later. This is acceptable only if G2 defines delivery generation as tied to later controller states, but the manual acceptance script should account for that timing.
- G2 test coverage should add direct assertions for events, no real runtime command usage, missing-run submit failure, status read-only behavior, and missing delivery packet collect failure.

## Rollback Note

Revert the G2 fake OpenCode runtime branch changes if these blocking issues cannot be fixed without crossing into G3. Do not start G3 Real OpenCode Runtime Manager until this report is updated to `passed`.

## Decision

G2 failed.

## Next Gate Unlock Status

G3 Real OpenCode Runtime Manager remains locked. Antigravity must fix the G2 blocking issues in `antigravity/g2-fake-opencode-runtime` and request a new Codex review.
