# AgentComOS v2.8.6 Phased Delivery Plan

> 中文备注：本计划保证项目分段落地、分段测试、分段验收。v2.8 全部功能保留，但必须按顺序实现，避免复杂度失控。

## Phase Overview

```text
0 Contract Baseline
1 Controller Minimum State Machine
2 Fake OpenCode Runtime
3 Real OpenCode Runtime Manager
4 tmux Hermes Worker Pool Fake E2E
5 Real Hermes Worker Runtime
6 Evidence / Delivery / GM Report
7 Operating Program / Task Frontier
8 Decision/Feynman Controlled Adoption
9 Loop Execution
10 Manual OS / Worker Evolution / Auto Versioner
11 Industrial Auto Governance
```

## Phase 0 — Contract Baseline

目标：项目包作为工程合同有效。

Codex gate：文档、schema、examples、tests、release manifest 一致。

Antigravity gate：不做大规模实现，只修 CLI 和测试工具问题。

## Phase 1 — Controller Minimum State Machine

目标：Controller 能创建 run、推进状态、写事件、恢复状态。

下一阶段解锁条件：

```text
run_status.yaml 可生成
events.jsonl append-only
tick 幂等
recover 可用
```

## Phase 2 — Fake OpenCode Runtime

目标：不用真实 OpenCode，跑通计划和交付包。

下一阶段解锁条件：

```text
fake opencode_job completed
delivery_packet.yaml 生成
logs 可审计
```

## Phase 3 — Real OpenCode Runtime Manager

目标：接入真实 `opencode serve` 和 `opencode run --attach`。

下一阶段解锁条件：

```text
serve healthcheck
job submit/collect
session ledger
stalled/timeout handling
```

## Phase 4 — tmux Hermes Worker Pool Fake E2E

目标：用 fake Hermes 证明 tmux Worker 生命周期。

下一阶段解锁条件：

```text
tmux session created
fake worker writes DONE.md
Controller collects outputs
worker_job completed
```

## Phase 5 — Real Hermes Worker Runtime

目标：真实 Hermes CLI 执行 Worker Invocation。

下一阶段解锁条件：

```text
hermes chat -Q -q 可执行
required outputs 可收集
failure_report 可记录
```

## Phase 6 — Evidence / Delivery / GM Report

目标：GM 可以向用户汇报。

下一阶段解锁条件：

```text
evidence_packet 完整
delivery_packet 完整
user_report_packet 完整
gm_report.md 可读
```

## Phase 7 — Operating Program / Task Frontier

目标：从 Operating Intent 生成 Operating Program，再生成可审计、可恢复、可线性推进的 Task Frontier。

下一阶段解锁条件：

```text
operating_program.yaml
task_frontier.yaml
task_frontier_index.yaml
frontier_status.yaml
controller tick --fake advances at most one frontier task
Evidence / Delivery / GM report include frontier state
```

## Phase 8 — Decision/Feynman Controlled Adoption

目标：实现三阶段采用策略。

```text
development_explicit
transition_assisted
industrial_auto
```

下一阶段解锁条件：

```text
开发期不自动扩散
显式指定可启用
工业化策略可自动判断
高风险任务强制 gate
```

## Phase 9 — Loop Execution

目标：批量循环任务可控执行。

下一阶段解锁条件：

```text
budget
stop conditions
max_parallel_workers
batch_result
next_frontier_candidates
```

## Phase 10 — Manual OS / Worker Evolution / Auto Versioner

目标：知识资产、自进化和版本治理闭环。

下一阶段解锁条件：

```text
manual release example
worker evolution example
change set
rollback target
version record
```

## Phase 11 — Industrial Auto Governance

目标：系统可自动判断何时启用 Decision / Feynman / Loop / Evolution。

商业化部署前必须通过：

```text
commercial deployment readiness checklist
backup/restore rehearsal
rollback rehearsal
secrets audit
cost budget ledger
GM approval flow
production healthcheck
```
