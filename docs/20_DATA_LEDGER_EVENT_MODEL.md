# Data Ledger and Event Model

> 中文备注：AgentComOS 要支持数据驱动开发和商业化部署审计，必须让每个关键动作都留下结构化事件。

## 1. Event Ledger

所有 run 事件写入：

```text
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/ledgers/events/
```

事件类型：

- run.created
- run.state_changed
- context.generated
- decision.requested
- decision.completed
- feynman.requested
- feynman.completed
- opencode.job.created
- opencode.job.completed
- worker.job.started
- worker.job.completed
- loop.batch.completed
- evidence.built
- delivery.built
- gm.report.generated
- version.finalized

## 2. Metrics Ledger

用于记录开发和运行质量：

- run_duration_seconds
- job_duration_seconds
- worker_success_rate
- feynman_veto_count
- decision_cost_usd
- worker_cost_usd
- loop_cost_usd
- delivery_latency_seconds
- rollback_count

## 3. Codex 审计要求

Codex 验收商业化部署版本时必须能回答：

- 每个 run 发生了什么？
- 哪些任务成功、失败、阻塞？
- 哪个 actor 触发了 Decision/Feynman？
- 是否超过预算？
- 是否有 rollback target？
- 用户是否收到清晰报告？
