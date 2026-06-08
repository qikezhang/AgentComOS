# Controller Implementation Spec — Phase 1 Priority

> 中文备注：Controller 是 AgentComOS 的稳定层和第一优先级实现模块。它不是 LLM Agent，不做业务判断，只负责状态机、调度、日志、恢复和交付物治理。

## 1. Controller 职责

Controller 必须负责：

```text
创建 run
维护 run_status.yaml
写 events.jsonl
生成或引用 runtime_context_bundle.yaml
调度 fake / real OpenCode job
执行 OpenCode 生成的 Worker Invocation
管理 tmux session
检查 timeout / stalled
收集 outputs
构建 Evidence Packet
构建 Delivery Packet
构建 User Report Packet
支持 recover
保证幂等
```

Controller 不负责：

```text
业务判断
方案选择
Worker 选择
Manual 内容判断
代码实现判断
用户沟通
```

## 2. Phase 1 最小命令

Phase 1 必须实现：

```bash
agentcomos run create --intent <operating_intent.yaml>
agentcomos run status --run <run_id>
agentcomos controller tick --run <run_id> --fake
agentcomos controller recover --run <run_id>
```

## 3. Run State Machine

最小状态：

```text
created
accepted
context_ready
planning
executing
evidence_verifying
delivery_ready
reported
completed
failed
blocked
paused
```

最小正常路径：

```text
created -> accepted -> context_ready -> planning -> executing -> evidence_verifying -> delivery_ready -> reported -> completed
```

异常路径：

```text
any -> failed
any -> blocked
any pausable -> paused
paused -> previous_state
failed -> retrying -> previous_retryable_state
blocked -> waiting_for_user -> previous_state
```

## 4. Job State Machine

```text
queued
running
completed
failed
stalled
cancelled
retrying
```

规则：

```text
queued -> running -> completed
queued/running -> failed
running + no_output_timeout -> stalled
stalled -> retrying
retrying -> queued
```

## 5. Worker Job State Machine

```text
created
tmux_started
running
outputs_detected
completed
failed
stalled
archived
```

完成条件：

```text
DONE.md exists
required_outputs exist
failure_report absent or non-blocking
timeout not exceeded
output_dir inside run worker_outputs
```

## 6. Event Log

每个动作必须写入 `events.jsonl`：

```json
{
  "event_id": "EVT-...",
  "run_id": "OI-...",
  "type": "run.created",
  "timestamp": "2026-06-08T00:00:00Z",
  "actor": "controller",
  "payload": {}
}
```

必须记录：

```text
run.created
run.state_changed
context.generated
opencode.job.created
opencode.job.completed
worker.job.started
worker.job.completed
evidence.built
delivery.built
gm.report.generated
run.completed
run.failed
```

## 7. 幂等规则

Controller 必须保证：

```text
同一个 run create 不重复创建目录
同一个 tick 不重复提交 OpenCode job
同一个 Worker Invocation 不重复启动 tmux，除非 retry_id 变化
collect 可重复执行
recover 不破坏已有状态
events.jsonl append-only
状态转移必须合法
```

## 8. Phase 1 Required Artifacts

```text
.agentcomos/runs/<run_id>/run_status.yaml
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/runs/<run_id>/timeline.yaml
.agentcomos/runs/<run_id>/evidence_packet/
.agentcomos/runs/<run_id>/delivery_packet.yaml
```

## 9. Phase 1 Acceptance Tests

Codex 必须验收：

```text
run create 生成 run_status.yaml
run create 写 run.created event
controller tick 推进状态
tick 可重复执行且不重复创建 job
recover 能恢复当前状态
非法状态转移失败
缺 operating_intent 失败
failed / blocked 状态可追踪
```

Antigravity 必须提交：

```text
实现代码
测试
fake E2E output
events.jsonl sample
run_status.yaml sample
rollback note
```
