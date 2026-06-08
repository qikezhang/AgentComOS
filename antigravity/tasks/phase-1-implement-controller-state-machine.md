# Antigravity Task: Phase 1 Controller Minimum State Machine

## Goal

Implement the minimum deterministic Controller state machine described in `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`.

## Required commands

```bash
agentcomos run create --intent <operating_intent.yaml>
agentcomos run status --run <run_id>
agentcomos controller tick --run <run_id> --fake
agentcomos controller recover --run <run_id>
```

## Required artifacts

```text
.agentcomos/runs/<run_id>/run_status.yaml
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/runs/<run_id>/timeline.yaml
```

## Tests to add

```text
test_run_create_generates_status
test_run_create_writes_event
test_tick_advances_state
test_tick_is_idempotent
test_recover_restores_state
test_invalid_transition_fails
```

## Evidence required

- Command output log
- Example generated run directory
- Test output
- Rollback note

## Do not implement yet

- Real OpenCode
- Real Hermes
- Loop Execution
- Manual Evolution
- Auto Versioner

## Handoff to Phase 2

When this task is complete, Antigravity must provide evidence for `codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md`. Codex must mark G1 as `passed` before `antigravity/tasks/phase-2-fake-opencode-runtime.md` can start.
