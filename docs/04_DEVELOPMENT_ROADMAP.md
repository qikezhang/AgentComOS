# AgentComOS v2.8.6 Development Roadmap

> 中文备注：本路线图用于驱动 Antigravity 分阶段实现，Codex 分阶段审计。v2.8 的完整功能不删除，但必须按阶段落地，禁止一次性大规模实现所有模块。

## 总原则

```text
Controller-first
Fake-runtime-first
Evidence-first
Codex-gated delivery
Controlled now, industrial automation later
```

## Phase 0 — Contract Baseline

目标：项目包本身可审计、可测试、可作为开发合同。

Antigravity 主要任务：不进入大规模 runtime 实现，只修复必要 CLI / 测试工具问题。

Codex 主要任务：审查文档、schema、examples、tests、acceptance gates、release manifest。

验收：

```bash
make compile
make test
make validate-examples
```

## Phase 1 — Controller Minimum State Machine

目标：实现最小可运行 Controller 状态机。

必须实现命令：

```bash
agentcomos run create
agentcomos run status
agentcomos controller tick
agentcomos controller recover
```

必须产物：

```text
.agentcomos/runs/<run_id>/run_status.yaml
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/runs/<run_id>/timeline.yaml
```

暂不接真实 OpenCode / Hermes，只用 fake runtime。

## Phase 2 — Fake OpenCode Runtime

目标：跑通 Controller → fake OpenCode job → Delivery Packet。

必须实现：

```bash
agentcomos opencode submit --run <run_id> --fake
agentcomos opencode collect --job <job_id>
```

必须产物：

```text
opencode_job.yaml
opencode_project_plan.yaml
delivery_packet.yaml
stdout.jsonl
```

## Phase 3 — Real OpenCode Runtime Manager

目标：接入真实 OpenCode serve / run --attach。

必须实现：

```bash
agentcomos opencode start
agentcomos opencode status
agentcomos opencode submit --run <run_id> --phase plan
agentcomos opencode collect --job <job_id>
agentcomos opencode recover
```

必须产物：

```text
opencode_job.yaml
opencode_session_ledger.yaml
stdout.jsonl
stderr.log
session_export.json
```

## Phase 4 — tmux Hermes Worker Pool Fake E2E

目标：用 fake Hermes 证明 tmux Worker 生命周期可控。

必须实现：

```bash
agentcomos worker start --fake
agentcomos worker status
agentcomos worker collect
agentcomos worker kill
```

必须证明：

```text
Controller 创建 tmux session
fake Hermes 读取 Worker Invocation
fake Hermes 写 DONE.md 和 result.yaml
Controller 检测完成
worker_job.yaml 变为 completed
logs 被收集
session 被归档或保留可 attach
```

## Phase 5 — Real Hermes Worker Runtime

目标：接入真实 Hermes CLI。

规则保持：

```text
Hermes Worker = tmux + hermes chat -Q -q
不是新 worker daemon
Worker Invocation 只能由 OpenCode 创建
Controller 只执行和监管
```

## Phase 6 — Evidence / Delivery / GM Report

目标：形成用户可读交付闭环。

必须实现：

```text
Evidence Packet Builder
Delivery Packet Builder
User Report Packet Builder
GM Report Renderer
```

GM 只读取 User Report Packet，不直接读取 Worker 原始输出。

## Phase 7 — Simple Operating Program

目标：跑通简单长期目标，但不启用复杂 Loop。

必须产物：

```text
operating_program.yaml
hourly_health_snapshot.yaml
daily_operating_packet.yaml
four_hour_operating_packet.yaml
```

## Phase 8 — Decision / Feynman Controlled Adoption

目标：开发期显式启用，过渡期辅助建议，工业化期自动策略。

采用策略：

```text
development_explicit: 用户显式指定 / 任务 required / 高风险强制
transition_assisted: 系统建议，GM/用户/策略确认
industrial_auto: 系统根据风险和历史质量自动判断
```

注意：本阶段不是恢复“开发期默认启用”，而是实现 adoption policy。

## Phase 9 — Loop Execution + Task Frontier

目标：支持用户明确要求或运营计划要求的批量循环任务。

必须约束：

```text
max_parallel_workers 默认 3
必须有 budget
必须有 stop conditions
每个 Loop task 必须有 Worker Invocation
每个 batch 必须输出 batch_result
```

## Phase 10 — Manual OS / Worker Evolution / Auto Versioner

目标：建立知识资产、自进化和版本治理闭环。

必须包含：

```text
Manual Update Proposal
Knowledge Card
Context Capsule
Worker Evaluation
Failure Attribution
Ratchet Decision
Change Set
Rollback Target
Version Record
```

## Phase 11 — Industrial Auto Governance

目标：从可控交付进入工业化自动治理。

系统可以自动判断启用：

```text
Decision Market
Feynman Engine
Loop Execution
Worker Evolution
Manual Update Proposal
Release Judge
Auto Versioner
```

但必须受限于：

```text
budget policy
risk policy
approval policy
evidence policy
rollback policy
GM report policy
```
