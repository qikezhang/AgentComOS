# AgentComOS v2.8.6 G1 to G2 Handoff

> 中文备注：本文件把“通过 G1 后进入 Fake OpenCode Runtime”写成硬门槛，避免 Antigravity 跳过 Controller-first 直接接真实 OpenCode / Hermes。

## 1. G1 Completion Definition

G1 通过前，必须完成：

```bash
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos controller tick --run <run_id> --fake
agentcomos run status --run <run_id>
agentcomos controller recover --run <run_id>
```

必须生成：

```text
.agentcomos/runs/<run_id>/run_status.yaml
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/runs/<run_id>/timeline.yaml
```

Codex 必须把 `codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md` 状态改为 `passed`。

## 2. G2 Unlock Conditions

只有满足以下条件才允许开始 G2：

1. G1 acceptance report = passed。
2. `make compile` 通过。
3. `make test` 通过。
4. `make validate-examples` 通过。
5. Controller tick 是幂等的。
6. Controller recover 能恢复 run 状态。
7. events.jsonl 包含 run.created、run.state_changed、delivery.built 或 fake delivery placeholder。

## 3. G2 Scope

G2 只实现 Fake OpenCode Runtime，不接真实 OpenCode。

必须实现：

```bash
agentcomos opencode submit --run <run_id> --fake
agentcomos opencode collect --job <job_id>
```

G2 目标是验证 Controller 能稳定管理 job 生命周期，而不是验证 OpenCode 本身。

## 4. Forbidden in G2

G2 禁止：

- 直接接真实 OpenCode。
- 直接接真实 Hermes。
- 启用 Loop Execution。
- 启用 industrial_auto Decision / Feynman。
- 绕过 Codex 验收进入 G3。
