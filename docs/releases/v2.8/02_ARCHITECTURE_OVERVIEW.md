# 02 Architecture Overview

## Current core flow

```text
Operating Intent
→ Operating Program
→ Task Frontier
→ Controller
→ Runtime / Worker
→ Evidence Packet
→ Delivery Packet
→ GM Report
→ Decision / Feynman / Manual OS / GM Discord Bridge
```

## v2.8 final production flow

```text
Real Discord Bot
→ Discord Inbound Artifact
→ GM Command
→ Risk Classifier
→ Permission Check
→ Controlled Executor
→ Operation Adapter
→ Execution Result
→ Evidence Packet
→ Delivery Packet
→ GM Report
→ Discord Reply / Operator Report
```

## Layer separation

Discord is the interaction layer.

GM Command is the control layer.

Controlled Executor is the policy and audit layer.

Operation Adapters are the execution layer.

No layer may bypass the Controlled Executor for shell/ssh/sudo/docker/systemctl operations.
