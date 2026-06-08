# Phase 6: Evidence, Delivery, and GM Report

> 中文备注：本任务负责实现 G6 的核心证据生成、交付包构建和 GM 报告功能。

## 目标

在 G1-G5 已具备 Controller、OpenCode、Hermes Worker 基础上，构建统一的 Evidence Packet、Delivery Packet 和 GM Report Packet 生成能力，让 GM 能够向用户清楚汇报：
1. 当前 run 做了什么。
2. 哪些任务成功。
3. 哪些任务失败或 blocked。
4. 使用了哪些 runtime。
5. 是否使用了 fake / real OpenCode。
6. 是否使用了 fake / real Hermes。
7. 生成了哪些 artifacts。
8. 有哪些证据支持交付结论。
9. 有哪些风险、缺口和下一步建议。
10. 这个 run 是否可以交付、需要重跑、还是需要人工介入。

## 验收标准

- `evidence build` 可以成功生成 `evidence_packet`，包括 `manifest.yaml`, `events_summary.yaml`, `runtime_summary.yaml`, `artifact_index.yaml`, `validation_summary.yaml`。
- `delivery build` 可以生成 `delivery_packet.yaml` 并引用 `evidence_packet`。
- `gm report` 可以生成 `gm_report.md` 和 `gm_report.yaml`。
- 构建过程必须是幂等的。
- 如果缺少必要的证据或 events，应当适当地进入 partial 或 failed 状态，不得伪造成功。
- 绝不能引入 Loop, Manual OS, Worker Evolution 等 G7+ 的能力。
