# Module 06 — Operating Program / Task Frontier

## Scope

G7 adds a controller-owned Operating Program and Task Frontier. The mechanism is auditable, resumable, and intentionally linear. It prepares work for fake OpenCode, fake Hermes, and reporting paths without implementing Loop Execution or recursive task expansion.

## Non-goals

- No Loop Execution.
- No recursive task expansion.
- No subagent delegation.
- No Manual OS.
- No Worker Evolution.
- No Auto Versioner.
- No Decision Market executor.
- No Feynman executor.
- No real OpenCode or real Hermes invocation.
- No Discord or direct user communication.

## Operating Program Contract

`operating_program.yaml` is generated inside `.agentcomos/runs/<run_id>/` from `operating_intent.yaml`. The Controller must not invent the objective; missing intent or missing objective fails safely.

Required fields:

```yaml
program_id: OP-<run_id>
run_id: <run_id>
created_by: controller
status: active
objective: "..."
source_intent: operating_intent.yaml
phases: []
constraints: {}
runtime_policy: {}
```

The G7 runtime policy defaults OpenCode and Hermes to fake. Real runtime requires an explicit flag and is outside the G7 controller tick path.

## Task Frontier Contract

`task_frontier.yaml` is generated from the active Operating Program. Each task has:

- `task_id`
- `title`
- `status`
- `priority`
- `depends_on`
- `runtime_hint`
- `invocation_type`
- `acceptance`
- `evidence_required`

Allowed task statuses:

```text
created
ready
blocked
running
completed
failed
skipped
```

Dependency rules:

- A task with incomplete dependencies is `blocked`.
- A task with completed dependencies may become `ready`.
- `running` requires a corresponding invocation or job artifact.
- `completed` requires all `evidence_required` files.
- `failed` requires `failure_reason`.
- `skipped` requires `skipped_reason`.

## Controller Tick Contract

`agentcomos controller tick --run <run_id> --fake` may:

1. Build `operating_program.yaml` if missing.
2. Build `task_frontier.yaml` if missing.
3. Select one ready frontier task.
4. Advance at most one task using fake OpenCode, fake Hermes, or G6 reporting builders.
5. Update `task_frontier.yaml`, `task_frontier_index.yaml`, `frontier_status.yaml`, `events.jsonl`, and `timeline.yaml`.

It must not loop, recurse, create subagents, start real OpenCode, start real Hermes, or create large task batches.

## Events

G7 appends controller-authored events:

```text
program.build.started
program.build.completed
program.build.failed
frontier.build.started
frontier.build.completed
frontier.build.failed
frontier.task.ready
frontier.task.started
frontier.task.completed
frontier.task.failed
frontier.task.blocked
frontier.status.updated
```

Events are append-only. Repeated build commands do not duplicate completed events when artifacts are already current.

## Rollback

Remove the G7 `program` and `frontier` packages, CLI commands, controller tick integration, tests, and this module document. Do not rewrite historical `.agentcomos/runs` operating data.

