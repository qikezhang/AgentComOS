# G2 — Fake OpenCode Runtime Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

passed

## Audit Metadata

- Audit time: 2026-06-08 21:14:49 CST (+0800)
- Auditor: Codex
- Branch reviewed: `antigravity/g2-fake-opencode-runtime`
- Commit reviewed: `d5406e05650f97e70b4933e72ea1a8920b3732bd`
- Working branch confirmed: `antigravity/g2-fake-opencode-runtime`
- Re-review context: Antigravity added `d5406e0 fix(opencode): generate delivery packet during fake submit` after the previous failed Codex re-review.

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
git status
git log --oneline -14
grep -R "opencode serve\|opencode run\|run --attach\|hermes chat\|tmux new-session\|tmux attach\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
make compile
make test
make validate-examples
```

Manual acceptance commands were re-run for `OI-TECHAI8-001`, including run creation, fake controller ticks, fake submit, fake status, fake collect, run status, recover, automatic tick integration, artifact checks, idempotency checks, and negative checks.

## Validation Results

- `make compile`: passed.
- `make test`: passed, `80 passed in 1.75s`.
- `make validate-examples`: passed.
- Manual `run create`: passed for `OI-TECHAI8-001`.
- Manual fake controller ticks to `planning`: passed.
- Manual fake submit: passed for `OCJ-OI-TECHAI8-001-001`.
- Manual fake status: passed and reported `status: completed`, `runtime: fake_opencode`, `fake_runtime: true`, `real_opencode_used: false`, `real_hermes_used: false`.
- Manual fake collect immediately after submit/status: passed.
- `run status`: passed.
- `controller recover`: passed.
- Controller fake tick integration: four fake ticks created exactly one fake OpenCode job and advanced to `executing`.
- No duplicate fake OpenCode job was created.

## Required Artifacts Checked

After the required manual and automatic G2 paths, the following artifacts existed:

- `.agentcomos/runs/OI-TECHAI8-001/opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_logs/OCJ-OI-TECHAI8-001-001.stdout.log`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_logs/OCJ-OI-TECHAI8-001-001.stderr.log`
- `.agentcomos/runs/OI-TECHAI8-001/opencode_outputs/opencode_project_plan.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/delivery_packet.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/events.jsonl`
- `.agentcomos/runs/OI-TECHAI8-001/timeline.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/run_status.yaml`

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
- Delivery packet references `opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml` and `opencode_outputs/opencode_project_plan.yaml`.
- Events include `opencode.job.created`, `opencode.job.started`, `opencode.job.completed`, `opencode.output.generated`, and `delivery.updated`.
- Timeline includes G2 OpenCode job events.

## Idempotency Checks

- Repeated submit after completion: passed. No duplicate job was created, job count remained 1, and hashes for job, events, timeline, plan, delivery, stdout log, and stderr log were unchanged.
- Repeated collect after delivery generation: passed. Completed job state and artifact hashes were unchanged.
- Repeated status: passed. Status output was stable and read-only; hashes for job, events, timeline, plan, delivery, and logs were unchanged.
- Repeated controller tick after completion: passed for job idempotency and state stability. It did not create duplicate OpenCode jobs and did not roll back run state.

## Negative Tests

- `agentcomos opencode status --job OCJ-DOES-NOT-EXIST`: failed as expected with exit code 2.
- `agentcomos opencode collect --job OCJ-DOES-NOT-EXIST`: failed as expected with exit code 2.
- `agentcomos opencode submit --run OI-DOES-NOT-EXIST --fake`: failed as expected with exit code 2.
- Missing-run submit did not create orphan artifacts under `.agentcomos/runs/OI-DOES-NOT-EXIST`.
- Completed job without `delivery_packet.yaml`: failed as expected with exit code 2.

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
- `test_opencode_submit_missing_run_fails_without_artifacts`
- `test_opencode_submit_missing_run_status_fails`
- `test_opencode_collect_missing_delivery_packet_fails_read_only`
- `test_fake_opencode_submit_generates_delivery_packet`
- `test_fake_opencode_collect_succeeds_after_submit_delivery_exists`
- `test_fake_submit_appends_delivery_updated_event`
- `test_fake_submit_updates_timeline_with_delivery_updated`
- `test_cli_opencode_submit_real_fails` partially covers no real OpenCode via CLI behavior.

Manual review additionally verified the exact required positive command sequence and status read-only behavior.

## Boundary Check

No runtime execution of real OpenCode, real Hermes, tmux Worker Pool, Loop Execution, Manual OS, Worker Evolution, Auto Versioner, Decision Market executor, or Feynman executor was found in the G2 fake runtime path.

Grep hits were reviewed:

- `src/agentcomos/cli.py` contains inherited command skeleton printers for `tmux new-session`, `hermes chat -Q -q`, and `opencode run --attach`; these print commands and are not called by `opencode submit/status/collect --fake`.
- `.agentcomos/opencode-runtime/runtime_policy.yaml` contains `opencode serve` as policy/config text, not a G2 runtime invocation.
- Documentation and task files contain future-phase references to real OpenCode, Hermes, and tmux; classified as documentation-only/non-runtime.

Scope review:

- Net diff against `main` does not delete tracked `.agentcomos/runs/OI-TECHAI8-001/*` artifacts and does not modify the G1 acceptance report.
- `.gitignore` now ignores `.agentcomos/runs/` and `.agentcomos/runtime/`; this is consistent with the rule that raw operating data is not a GitTree release object.
- `tests/test_v286_phase_gate_package.py` was adjusted to accept reports that have `Blocking Issues`; this is report-validation support and not runtime implementation.

Confirmations:

- Real OpenCode used: no.
- Real Hermes used: no.
- tmux Worker Pool implemented: no.
- Loop / Manual / Worker Evolution / Auto Versioner implemented: no.

## Blocking Issues

None.

## Resolved Previous Blocking Issues

- Missing-run submit now fails and does not create orphan job artifacts.
- Collect now fails for a completed job when `delivery_packet.yaml` is missing.
- Net branch diff no longer contains the previous out-of-scope G1 report modification or tracked run artifact deletion.
- The required positive manual submit/status/collect sequence now passes because fake submit generates/updates `delivery_packet.yaml`.

## Non-blocking Issues

- `delivery.updated` may appear more than once after later controller ticks rebuild delivery; this is not blocking for G2 but should remain intentional.

## Rollback Note

If regression is found before merge, revert the G2 fake OpenCode runtime changes and keep G3 locked until G2 is re-passed.

## Decision

G2 passed.

## Next Gate Unlock Status

G3 Real OpenCode Runtime Manager may start after merge.
