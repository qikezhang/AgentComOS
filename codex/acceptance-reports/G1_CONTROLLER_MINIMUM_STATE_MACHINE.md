# G1 - Controller Minimum State Machine Acceptance Report

> Maintained by Codex. G1 must be `passed` before G2 Fake OpenCode Runtime may start.

## Status

failed

## Audit Metadata

- Audit time: 2026-06-08 15:40:31 CST +0800
- Auditor: Codex
- Audited branch: `antigravity/g1-controller-state-machine`
- Audited commit: `825f9f201404b0323bd40b9c92a52db96deb8531`
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

- `git status`: clean before audit run.
- `git log --oneline -5`: `825f9f2 feat(controller): implement G1 minimum state machine` at HEAD.
- `make compile`: passed.
- `make test`: passed, `58 passed in 2.87s`.
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
- `run status`: returned status successfully, but mutated artifacts; see blocking issue G1-BLOCK-001.
- First fake ticks: `created -> accepted -> context_ready`.
- `recover`: restored state to `context_ready` from events.
- Further fake ticks reached `completed`.
- Completed-state tick: preserved `run_status.yaml`, `delivery_packet.yaml`, and `evidence_packet/manifest.yaml`; appended tick events and rewrote `timeline.yaml`.
- Final `run status`: showed `state: completed`.
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
- `evidence_packet/manifest.yaml`: includes `fake_runtime: true`, `real_opencode_used: false`, and `real_hermes_used: false`.
- `delivery_packet.yaml`: exists with `status: completed`.

## Idempotency Checks

- Initial `run create` created state `created`.
- Repeated `run create` did not overwrite the existing run.
- Fake tick advanced at most one implemented transition per command.
- State did not regress during the manual path.
- `recover` did not delete events.
- Completed-state tick did not change final state or rebuild the manifest/delivery packet content.
- `events.jsonl` was written using append mode in `src/agentcomos/controller/events.py`.
- `run status` is not artifact-idempotent: it appends `run.status_read` and rewrites `timeline.yaml`.

## Boundary Check

Command search found pre-existing CLI skeleton strings in `src/agentcomos/cli.py`:

- `tmux new-session -d`
- `hermes chat -Q -q`
- `opencode run --attach`

These command skeletons existed before the G1 branch according to `git diff main...HEAD -- src/agentcomos/cli.py`; they were not introduced by this branch. G1 Controller code under `src/agentcomos/controller/*` contains no `opencode`, `hermes`, `tmux`, `subprocess`, `os.system`, or `Popen` usage. Codex therefore did not find evidence that the G1 Controller runtime calls real OpenCode, real Hermes, or tmux.

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

## Test Coverage Review

Covered directly or equivalently:

- `test_run_create_generates_status`: covered directly.
- `test_run_create_is_idempotent`: covered directly.
- `test_run_status_reads_status`: covered by `test_cli_run_status`.
- `test_controller_tick_fake_advances_state`: covered directly.
- `test_controller_tick_fake_reaches_completed`: covered directly.
- `test_controller_tick_is_idempotent_after_completed`: covered directly, but weakly asserts only final state.
- `test_controller_recover_restores_state`: covered directly.
- `test_missing_intent_fails`: covered directly.
- `test_delivery_packet_is_created`: covered as part of `test_controller_tick_fake_reaches_completed`.
- `test_evidence_packet_manifest_is_created`: covered as part of `test_controller_tick_fake_reaches_completed`.

Coverage gaps:

- `test_status_does_not_mutate_state` only checks `run_status.yaml` state equality; it does not catch mutation of `events.jsonl` and `timeline.yaml`.
- `test_invalid_transition_fails` only checks missing run failure, not an actual illegal state transition.
- `test_events_jsonl_is_appended` is not directly covered.
- `test_timeline_yaml_is_updated` is not directly covered for state transitions.
- `test_no_real_opencode_or_hermes_usage` is an empty/pass-only test.

## Blocking Issues

### G1-BLOCK-001 - `run status` mutates artifacts

Requirement: `run status` must not modify artifacts.

Observed:

- Before `run status`, `events.jsonl` had 1 line and hash `c9b60cd49015ec83b122beff5843103520a8d871`.
- After `run status`, `events.jsonl` had 2 lines and hash `49e81531d5d862c19d3d6687cf04ddb212417211`.
- `timeline.yaml` hash changed from `0581ace4e8d93cfb330432b28cf23f9172d685dc` to `0ca30b871f5e4034162a4fe40036e9c31834bb1c`.

Code reference: `src/agentcomos/controller/runner.py` appends `run.status_read` and rebuilds timeline in `handle_run_status`.

### G1-BLOCK-002 - Fake normal path skips required `reported` state

Requirement from `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`:

```text
created -> accepted -> context_ready -> planning -> executing -> evidence_verifying -> delivery_ready -> reported -> completed
```

Observed fake path:

```text
created -> accepted -> context_ready -> planning -> executing -> evidence_verifying -> delivery_ready -> completed
```

Code reference: `src/agentcomos/controller/state.py` maps `delivery_ready` directly to `completed`.

### G1-BLOCK-003 - Required negative/idempotency coverage is incomplete

The test suite passes, but it does not fully enforce the G1 acceptance contract:

- No actual illegal transition test.
- No artifact-level no-mutation test for `run status`.
- No direct append-only test for `events.jsonl`.
- No direct state-transition update test for `timeline.yaml`.
- No substantive no-real-OpenCode/Hermes test; current test is pass-only.

## Non-blocking Issues

- The audit grep finds pre-existing OpenCode/Hermes/tmux command skeletons in `src/agentcomos/cli.py`. They are not G1 branch additions and are not called by `src/agentcomos/controller/*`, but future G2/G3 reviews should keep this boundary explicit.

## Rollback Note

If this G1 branch is not merged, no runtime deployment rollback is required. Local generated audit artifacts under `.agentcomos/runs/OI-TECHAI8-001` can be removed and regenerated.

## Decision

failed

G1 is blocked. G2 Fake OpenCode Runtime may not start until the blocking issues above are fixed and Codex re-runs acceptance.

## Next Gate Unlock Status

Locked. Antigravity must fix G1 blocking issues in `antigravity/g1-controller-state-machine` and request a new Codex G1 review.

## Antigravity Implementation Notes

- Fixed G1-BLOCK-001 by making status read-only
- Fixed G1-BLOCK-002 by adding reported to get_next_fake_state
- Fixed G1-BLOCK-003 by adding comprehensive test_controller_g1_state_machine.py

## Codex Findings
See Blocking Issues and Non-blocking Issues above.
