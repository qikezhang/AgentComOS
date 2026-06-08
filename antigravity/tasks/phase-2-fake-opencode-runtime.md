# Antigravity Task — Phase 2 Fake OpenCode Runtime

> 中文备注：本任务只能在 G1 Controller Minimum State Machine 通过后开始。不得跳过 fake runtime 直接接真实 OpenCode。

## Locked Until

`codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md` status is `passed`.

## Goal

Implement fake OpenCode runtime to validate Controller job lifecycle before integrating real OpenCode.

## Required Commands

```bash
agentcomos opencode submit --run <run_id> --fake
agentcomos opencode collect --job <job_id>
```

## Required Outputs

```text
.agentcomos/runs/<run_id>/opencode_jobs/<job_id>/opencode_job.yaml
.agentcomos/runs/<run_id>/opencode_jobs/<job_id>/stdout.jsonl
.agentcomos/runs/<run_id>/opencode_project_plan.yaml
.agentcomos/runs/<run_id>/delivery_packet.yaml
```

## Forbidden

- Do not integrate real OpenCode in this phase.
- Do not start Hermes.
- Do not start Loop Execution.
- Do not enable industrial_auto Decision/Feynman.

## Acceptance Gate

Codex validates using `codex/acceptance-reports/G2_FAKE_OPENCODE_RUNTIME.md`.
