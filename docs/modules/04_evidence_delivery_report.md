# Module 04: Evidence, Delivery, and GM Report

> 中文备注：本模块负责将零散的 events 和 runtime 状态汇总为统一的交付凭证。

## 架构职责

- **Evidence Builder**: 扫描 `events.jsonl` 和 `artifacts`，生成不可篡改的证据摘要（Events, Runtime, Artifacts, Validation）。
- **Delivery Builder**: 组合 Evidence 和 GM Report，生成最终的交付包 `delivery_packet.yaml`。
- **GM Report**: 根据收集到的证据，生成人类可读的 `gm_report.md` 和机器可读的 `gm_report.yaml`，明确列出使用了哪些（fake/real）环境，以及交付结论。

## 核心约束

1. 必须基于 `events.jsonl`，不得凭空捏造事件。
2. 必须明确披露是否使用了 `fake` runtime 或 real runtime 的 `unavailable` 状态。
3. 缺失关键文件时，必须进入 partial 或 failed 状态。
4. 所有的 Builder 操作都必须是幂等的。
