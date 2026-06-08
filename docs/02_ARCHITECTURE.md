# AgentComOS Architecture

## System flow

```text
User -> Discord -> GM Hermes -> Controller -> OpenCode Runtime
OpenCode -> Decision Market -> Feynman -> Task Frontier / Loop / Worker Invocation
Controller -> tmux Hermes Worker -> Worker outputs -> OpenCode synthesis
OpenCode -> Evidence Packet -> GitTree / Auto Versioner -> Delivery Packet -> GM -> User
```

## Module boundaries

### GM

User-facing operator. Can create Operating Intent and Daily Operating Packet. Cannot call Workers.

### Controller

Deterministic runtime orchestrator. Executes, monitors, validates. Does not decide which Worker to use.

### OpenCode

Engineering runtime and Worker Manager. Creates Decision requests, Worker Invocations, Loop Execution Requests, Delivery Packets.

### Hermes Worker

A tmux-launched Hermes CLI instance. Reads one invocation and writes outputs.

### Decision Market

Pre-execution option discovery and decision. Used for any task with uncertainty.

### Feynman Engine

Default adversarial check for non-trivial tasks. Applies before execution, during loop batches, and after evidence generation.

### Task Frontier

Controls task graph and next batch selection.

### Loop Execution Engine

Runs finite, budgeted task batches.

### Manual OS

Company knowledge base and operating manual. Updated only through evidence, proposal, audit, release, version.

## Data flow rules

- Raw Worker outputs are not user-facing.
- GM sees Delivery Packet and User Report Packet.
- Raw operating data is stored in ledgers or warehouse, not GitTree release objects.
- Evidence Packet is the completion basis.
