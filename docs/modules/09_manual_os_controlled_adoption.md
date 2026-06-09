# Module 09: Manual OS Controlled Adoption

## Scope
G10 introduces the explicit manual OS action protocol layer. This allows AgentComOS to identify tasks requiring manual intervention (such as SSHing into a VPS, running docker compose, modifying systemd configurations, or running commands with sudo) and pause execution until explicitly approved and reported back by an operator.

## Non-goals
- No automatic execution of shell commands.
- No automatic execution of os.system, subprocess, or paramiko.
- No automatic ssh connections.
- No automatic docker or systemctl management.
- No background unsupervised daemon execution of Manual OS tasks.
- No Discord Bridge integration (G11).
- No GM online bidirectional communication (G11).
- No Worker Evolution.
- No Auto Versioner.

## Contract
When a task in the `task_frontier.yaml` contains `manual_os_required: true`:
1. The system must not execute the task automatically.
2. The operator must explicitly request the manual OS action using `agentcomos manual-os request`. This generates a `manual_os_request.yaml` artifact.
3. The operator must approve the request using `agentcomos manual-os approve`. This generates a `manual_os_approval.yaml` artifact. Alternatively, they can reject it.
4. The operator performs the manual work in their own environment. AgentComOS does NOT observe or perform the work.
5. The operator reports the result using `agentcomos manual-os result`. This generates a `manual_os_result.yaml` artifact.
6. Only when `manual_os_result.yaml` has `status: completed` will the task become unblocked.
7. An audit can be generated using `agentcomos manual-os audit` summarizing the process in `manual_os_audit.md`.

## Integration Points
- **Controller/Frontier**: `frontier status` shows `awaiting_manual_os`. `controller tick` will not execute an `awaiting_manual_os` task.
- **Loop Execution**: `loop run` will stop with `stop_reason: awaiting_manual_os` and record a blocked tick in `loop_trace.yaml`.
- **Evidence/Delivery/GM Report**: The artifacts are indexed and disclosed. The system explicitly claims it did NOT execute real commands.
