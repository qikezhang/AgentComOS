# AgentComOS v2.8 Engineering Specification

This document converts the product specification into buildable engineering requirements.

## 1. Engineering goal

Build a controllable, testable, Docker-deployable platform where:

- GM receives user goals and emits Operating Intents or Daily Operating Packets.
- Controller creates runs, worktrees, context bundles, and dispatches OpenCode.
- OpenCode classifies tasks, applies Decision Market when uncertainty exists, applies Feynman checks for non-trivial tasks, and creates Worker Invocation only when needed.
- Controller executes Worker Invocation through tmux + Hermes CLI.
- Worker outputs return to OpenCode, not GM.
- Controller mechanically verifies outputs and Evidence Packet completeness.
- GitTree / Auto Versioner determine version, release, and rollback objects.

## 2. Required implementation units

### 2.1 Controller CLI

Minimum commands:

```bash
agentcomos doctor
agentcomos validate <run_dir>
agentcomos run create --intent <intent.yaml>
agentcomos opencode start
agentcomos opencode submit --run <run_id> --phase plan
agentcomos worker start-tmux --run <run_id> --task <task_id> --worker <worker_id> --invocation <path>
agentcomos worker status --run <run_id>
agentcomos evidence verify --run <run_id>
```

### 2.2 Runtime manager

- Ensure OpenCode server is reachable.
- Submit `opencode run --attach` commands.
- Capture stdout/json logs.
- Record session metadata.

### 2.3 Hermes Worker Pool

- Read Worker Invocation.
- Create tmux session name.
- Execute Hermes CLI.
- Track `DONE.md`, required outputs, log growth, timeout and stalled state.

### 2.4 Decision Market

- Task Classification.
- Decision Need Score.
- skip / mini / standard / full decision request.
- Proposal, scoring, critic, synthesis and final decision contracts.

### 2.5 Feynman Engine

- skip only for trivial deterministic tasks.
- lite / standard / full checks.
- Must run pre-execution for non-trivial tasks.
- Must run as batch gate for Loop Execution.
- Must run or delegate to Evidence Audit before release.

## 3. Test strategy

Every module must include:

- schema validation test
- positive example
- negative example
- acceptance criterion
- evidence artifact expectation
