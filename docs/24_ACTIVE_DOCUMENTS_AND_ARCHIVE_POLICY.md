# AgentComOS v2.8.6 Active Documents and Archive Policy

> 中文备注：本文件定义当前活跃文档、历史文档和 Codex / Antigravity 的引用优先级，避免历史版本文档造成实现偏差。

## 1. Active Implementation Documents

Antigravity 进行代码开发时，必须优先阅读并遵守以下活跃文档：

1. `README.md`
2. `AGENTS.md`
3. `docs/00_PRODUCT_SPEC_V2_8.md`，但仅作为完整产品目标基线
4. `docs/15_CODEX_ANTIGRAVITY_COLLABORATION.md`
5. `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
6. `docs/17_PHASED_DELIVERY_PLAN.md`
7. `docs/18_ACCEPTANCE_GATES.md`
8. `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md`
9. `docs/20_DATA_LEDGER_EVENT_MODEL.md`
10. `docs/21_COMMERCIAL_DEPLOYMENT_READINESS.md`
11. `docs/22_RUNTIME_INSTALLATION_EVOLUTION.md`
12. `docs/23_PR_AND_REVIEW_WORKFLOW.md`
13. `docs/25_PHASE_ACCEPTANCE_REPORTING.md`
14. `docs/26_G1_TO_G2_HANDOFF.md`
15. `docs/27_RUNTIME_JOB_ROUTING_RULES.md`

## 2. Historical Reference Documents

以下文档只作为历史记录，不得作为当前实现依据：

- `docs/11_ENGINEERING_CONTRACT_V2_8_3.md`
- `docs/13_CONTRACT_HARDENING_V2_8_4.md`
- `docs/archive/11_ENGINEERING_CONTRACT_V2_8_3.md`
- `docs/archive/13_CONTRACT_HARDENING_V2_8_4.md`

## 3. Conflict Resolution

如文档存在冲突，优先级如下：

```text
1. RELEASE_MANIFEST.md
2. AGENTS.md
3. docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md
4. docs/17_PHASED_DELIVERY_PLAN.md
5. docs/18_ACCEPTANCE_GATES.md
6. docs/27_RUNTIME_JOB_ROUTING_RULES.md
7. docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md
8. docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md
9. docs/00_PRODUCT_SPEC_V2_8.md
```

`docs/00_PRODUCT_SPEC_V2_8.md` 保留 v2.8 完整愿景，但 v2.8.6 的开发期策略以 active implementation docs 为准。

## 4. Codex G0 Review Requirement

Codex 在 G0 必须执行 active docs review：

- 确认所有 active docs 版本号一致。
- 确认历史文档已标记 archived。
- 确认 Antigravity 不会从历史文档读取当前实现策略。
- 确认 Decision / Feynman 采用策略为 Explicit -> Assisted -> Industrial Auto。
- 输出 `codex/acceptance-reports/G0_CONTRACT_BASELINE.md`。
