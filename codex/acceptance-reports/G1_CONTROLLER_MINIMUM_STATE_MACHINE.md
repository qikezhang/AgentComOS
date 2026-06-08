# G1 - Controller Minimum State Machine Acceptance Report

> Maintained by Codex. G1 must be `passed` before G2 Fake OpenCode Runtime may start.

## Status

passed

## Audit Metadata

- Audit time: 2026-06-08 15:55:34 CST +0800
- Auditor: Codex
- Audited branch: `antigravity/g1-controller-state-machine`
- Audited commit: `4eadfe7080f0ff8171abd11fe3d1e44fa330c824`
- Working branch confirmed: `antigravity/g1-controller-state-machine`

## Inputs Reviewed

- `AGENTS.md`
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/26_G1_TO_G2_HANDOFF.md`
- `antigravity/tasks/phase-1-implement-controller-state-machine.md`
- `codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md`

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g1-controller-state-machine
git pull origin antigravity/g1-controller-state-machine
git status
git log --oneline -5
grep -R "opencode serve\|opencode run\|hermes chat\|tmux new-session\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
make compile
make test
make validate-examples
```

Results:

- `git status`: clean before manual audit run.
- `git log --oneline -5`: `4eadfe7 fix(controller): satisfy G1 codex blocking issues` at HEAD.
- `make compile`: passed.
- `make test`: passed, `59 passed in 1.85s`.
- `make validate-examples`: passed.

Note: bare `agentcomos` was not on PATH in the audit shell, so manual CLI checks used the installed equivalent entrypoint `./.venv/bin/agentcomos`.

## Manual Acceptance Results

Manual run used:

```bash
rm -rf .agentcomos/runs/OI-TECHAI8-001
./.venv/bin/agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
./.venv/bin/agentcomos run status --run OI-TECHAI8-001
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller recover --run OI-TECHAI8-001
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos controller tick --run OI-TECHAI8-001 --fake
./.venv/bin/agentcomos run status --run OI-TECHAI8-001
```

Observed results:

- `run create`: passed; initial `run_status.yaml` had `state: created`.
- `run status`: passed and was artifact-read-only; `run_status.yaml`, `events.jsonl`, and `timeline.yaml` hashes were unchanged.
- First fake ticks: `created -> accepted -> context_ready`.
- `recover`: restored state to `context_ready` from events during the early path.
- Further fake ticks reached `completed` through `reported`.
- Completed-state tick: preserved `run_status.yaml`, `delivery_packet.yaml`, and `evidence_packet/manifest.yaml`; no additional `run.state_changed` was emitted.
- Final `run status`: showed `state: completed`.
- Recover after deleting `run_status.yaml`: restored `state: completed` from `events.jsonl` and did not delete events.
- Duplicate `run create`: did not overwrite existing `run_status.yaml`, `events.jsonl`, or `timeline.yaml`.
- Missing intent: `./.venv/bin/agentcomos run create --intent /tmp/not-exist-operating-intent.yaml` failed with exit code 2 and did not create an abnormal run.

## Required Artifacts Checked

All required G1 artifacts were present after manual completion:

- `.agentcomos/runs/OI-TECHAI8-001/run_status.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/events.jsonl`
- `.agentcomos/runs/OI-TECHAI8-001/timeline.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/evidence_packet/manifest.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/delivery_packet.yaml`

Content checks:

- Final `run_status.yaml`: `state: completed`.
- Final `timeline.yaml`: `current_state: completed`, consistent with `run_status.yaml`.
- `events.jsonl`: valid JSONL append log was produced.
- `timeline.yaml`: includes the expected state path through `reported`.
- `evidence_packet/manifest.yaml`: includes `fake_runtime: true`, `real_opencode_used: false`, and `real_hermes_used: false`.
- `delivery_packet.yaml`: exists with `status: completed`.

## Idempotency Checks

- Initial `run create` created state `created`.
- Repeated `run create` did not overwrite the existing run.
- Fake tick advanced one implemented state per command.
- State did not regress during the manual path.
- `run status` did not modify artifacts.
- `recover` did not delete events.
- Completed-state tick did not change final state or rebuild the manifest/delivery packet content.
- `events.jsonl` is append-only for controller events.
- `timeline.yaml` and `run_status.yaml` agreed on final state.

## Boundary Check

The required grep found pre-existing CLI skeleton strings in `src/agentcomos/cli.py` and documentation examples:

- `tmux new-session -d`
- `hermes chat -Q -q`
- `opencode run --attach`
- `opencode serve`

These command skeletons existed before the G1 implementation branch and are not called by the G1 Controller implementation. G1 Controller code under `src/agentcomos/controller/*` contains no `opencode`, `hermes`, `tmux`, `subprocess`, `os.system`, or `Popen` usage.

Confirmed for G1 Controller implementation:

- Real OpenCode used: no.
- Real Hermes used: no.
- tmux Worker Pool implemented: no.
- Loop Execution implemented: no.
- Manual OS implemented: no.
- Worker Evolution implemented: no.
- Auto Versioner implemented: no.
- Decision Market executor implemented: no.
- Feynman executor implemented: no.
- v2.8 product boundary changed: no.

## Test Coverage Review

Covered directly or equivalently:

- `test_run_create_generates_status`: covered directly.
- `test_run_create_is_idempotent`: covered by `test_run_create_does_not_overwrite_existing_run`.
- `test_run_status_reads_status`: covered by `test_cli_run_status`.
- `test_status_does_not_mutate_state`: covered by `test_run_status_is_read_only`, including `events.jsonl` and `timeline.yaml`.
- `test_controller_tick_fake_advances_state`: covered by `test_cli_controller_tick`.
- `test_controller_tick_fake_reaches_completed`: covered by `test_fake_tick_path_includes_reported`.
- `test_controller_tick_is_idempotent_after_completed`: covered by `test_completed_tick_is_idempotent`.
- `test_controller_recover_restores_state`: covered by manual recover checks and partially by `test_recover_does_not_delete_events`.
- `test_invalid_transition_fails`: covered by `test_invalid_transition_fails_or_is_blocked`.
- `test_missing_intent_fails`: covered directly.
- `test_events_jsonl_is_appended`: covered by manual event count checks and append-mode implementation review.
- `test_timeline_yaml_is_updated`: covered by manual timeline content check.
- `test_evidence_packet_manifest_is_created`: covered by `test_completed_tick_is_idempotent` and manual artifact check.
- `test_delivery_packet_is_created`: covered by `test_completed_tick_is_idempotent` and manual artifact check.
- `test_no_real_opencode_or_hermes_usage`: covered by boundary grep and implementation review; the existing CLI test remains lightweight.

Residual test note:

- A direct unit test for deleting `run_status.yaml` and asserting recover restores the state would make the suite stronger, but manual acceptance passed and this is not blocking for G1.

## Codex Findings

None.

## Blocking Issues

None.

## Non-blocking Issues

- Pre-existing command skeletons for future OpenCode/Hermes/tmux phases remain in `src/agentcomos/cli.py`; they are outside the G1 Controller runtime path. Future G2/G3/G4 reviews should continue to keep this boundary explicit.

## Rollback Note

No runtime deployment rollback is required for G1. If needed, remove generated run artifacts under `.agentcomos/runs/<run_id>` and rerun `agentcomos run create` plus fake ticks.

## Decision

passed

G1 passed.
G2 Fake OpenCode Runtime may start.

## Next Gate Unlock Status

Unlocked after merge. Antigravity may start G2 Fake OpenCode Runtime after G1 is merged.
