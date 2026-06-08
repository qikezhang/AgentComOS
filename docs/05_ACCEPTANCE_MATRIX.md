# AgentComOS v2.8.6 Acceptance Matrix

> 中文备注：本矩阵是 Codex 阶段验收主表。任何阶段没有 schema、example、正例测试、负例测试、验收命令和 evidence artifact，不允许进入下一阶段。

| Gate | 阶段 | Antigravity 输出 | Codex 验收重点 | 必须通过命令 | 阻塞下一阶段 |
|---|---|---|---|---|---|
| G0 | Contract Baseline | 无大规模 runtime 实现；修复契约包问题 | 文档版本一致、schema/examples/tests 可用 | `make compile && make test && make validate-examples` | 是 |
| G1 | Controller Minimum State Machine | `run create/status`, `controller tick/recover`, run_status, events | 状态转移合法、幂等、recover 可用 | `pytest tests -q` + CLI E2E | 是 |
| G2 | Fake OpenCode Runtime | fake submit/collect、opencode_job、delivery_packet | fake job 状态、日志、交付包完整 | fake OpenCode E2E | 是 |
| G3 | Real OpenCode Runtime Manager | start/status/submit/collect/recover | session ledger、stdout/stderr、timeout/stalled | real/fake 双模式测试 | 是 |
| G4 | tmux Hermes Worker Fake E2E | tmux start/status/collect/kill、fake DONE.md | session 命名、DONE 检测、output_dir、worker_job 状态 | tmux fake worker E2E | 是 |
| G5 | Real Hermes Worker Runtime | `tmux + hermes chat -Q -q` 实接 | 不得创建自定义 worker daemon；输出可收集 | real Hermes smoke test | 是 |
| G6 | Evidence / Delivery / GM Report | evidence_packet、delivery_packet、user_report_packet、gm_report | GM 不读原始 Worker 输出；报告清楚状态/风险/下一步 | report rendering tests | 是 |
| G7 | Simple Operating Program | hourly/daily/four-hour packet | 运营节奏可触发、状态可汇报 | scheduler fake E2E | 否 |
| G8 | Decision/Feynman Adoption | adoption policy executor | development_explicit 不自动扩散；industrial_auto 可策略启用 | stage adoption tests | 是 |
| G9 | Loop + Task Frontier | loop_request、loop_batch、batch_result | budget/stop/max_parallel_workers/worker_invocations 一致 | loop contract tests | 是 |
| G10 | Manual / Worker Evolution / Auto Versioner | manual update、worker eval、ratchet、change set | 不允许 GM/Worker 直接改 Manual；patch 必须 ratchet；release 必须 rollback | governance tests | 是 |
| G11 | Industrial Auto Governance | 自动治理策略、预算、审批、回滚 | 商业化部署前的安全门槛 | commercial audit checklist | 是 |

## 每个 Gate 的强制结构

每个 Gate 必须有：

```text
1. 输入文件
2. 输出文件
3. CLI 命令
4. 正例 example
5. 负例 test
6. evidence artifact
7. Codex review report
8. Antigravity implementation report
9. rollback note
10. 下一阶段解锁条件
```

## Gate 失败处理

```text
P0 失败：停止后续开发，先修契约或状态机。
P1 失败：可继续文档完善，但不得合并 runtime 实现。
P2 失败：记录风险，可进入下阶段但必须进入 backlog。
```
