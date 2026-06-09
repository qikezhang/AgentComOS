# Module 08: Loop Execution

## Scope
G9 introduces a bounded, controlled loop execution mechanism. It allows the AgentComOS to execute multiple rounds of task advancement within a single run, provided strict budget constraints and stop conditions are met.

## Core Capabilities
- **Bounded Loop**: The loop is restricted by a `max_ticks` budget explicitly provided by the caller. Infinite loops are not supported.
- **Fake Runtime Only**: Loop execution currently only operates under `fake` runtime. Real Hermes and OpenCode are explicitly disabled.
- **Controlled Advancement**: Each tick within a loop execution advances at most one frontier task.
- **Auditable**: Every tick generates a corresponding trace entry in `loop_trace.yaml`.
- **Halted on Blocker**: The loop automatically halts if a task requires explicit human decision (`awaiting_decision`) or Feynman validation (`awaiting_feynman`), deferring these actions per G8 rules.
- **Recoverable**: A loop's state can be rebuilt and safely recovered from `loop_trace.yaml` if interrupted.

## Limitations
- No automatic infinite daemon loop.
- No recursive task expansion.
- No dynamic worker evolution or generation.
- No auto versioner.
- No real discord or real hermes invocation.

## Stop Conditions
The loop terminates under the following conditions:
- `max_ticks_reached`: The allocated budget of ticks has been exhausted.
- `no_ready_task`: All tasks in the frontier are either completed, blocked, or failed.
- `awaiting_decision`: A task requires a human decision.
- `awaiting_feynman`: A task requires a Feynman executor check.
- `failed_task`: A task has failed to complete successfully.
- `max_task_advancements_reached`: The specified maximum number of advanced tasks has been reached.

## Artifacts
- `loop_plan.yaml`: Defines loop budget and constraints.
- `loop_status.yaml`: Tracks the current state and stopping reasons.
- `loop_trace.yaml`: Appended history of each tick.
- `loop_summary.md`: GM readable markdown summarizing the loop.
