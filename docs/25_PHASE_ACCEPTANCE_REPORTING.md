# AgentComOS v2.8.6 Phase Acceptance Reporting

> 中文备注：Codex 不只负责 G0/G1，而是负责 **所有 Phase / Gate 的验收报告**。Antigravity 每个阶段交付后，Codex 必须根据本文件补充或执行验收报告。

## 1. Rule

每个 Phase 必须有一个 Codex Acceptance Report：

```text
codex/acceptance-reports/G0_CONTRACT_BASELINE.md
codex/acceptance-reports/G1_CONTROLLER_MINIMUM_STATE_MACHINE.md
...
codex/acceptance-reports/G11_INDUSTRIAL_AUTO_GOVERNANCE.md
```

这些报告可以先以 `pending` 状态存在，但对应 Phase 开发前必须由 Codex 补全细则，对应 Phase 合并前必须由 Codex 执行并改为 `passed` 或 `failed`。

## 2. Report Required Sections

每份报告必须包含：

```text
Gate ID
Phase name
Status: pending / in_review / passed / failed / blocked
Scope
Inputs reviewed
Commands executed
Required artifacts checked
Positive tests
Negative tests
Evidence artifacts
Antigravity implementation report link
Codex findings
Blocking issues
Non-blocking issues
Rollback note
Decision
Next gate unlock status
```

## 3. Codex Duties Across All Phases

Codex 必须：

1. 在 Phase 开始前补齐该 Phase 的验收细则。
2. 在 Antigravity 提交 PR 后执行测试和审计。
3. 更新 `docs/05_ACCEPTANCE_MATRIX.md` 和 `docs/18_ACCEPTANCE_GATES.md`。
4. 记录 evidence 是否足够。
5. 明确是否允许进入下一 Phase。

## 4. Antigravity Duties

Antigravity 必须提交：

1. 实现说明。
2. 命令输出。
3. 生成的 artifacts。
4. 测试结果。
5. 失败和回滚说明。

## 5. Current Strategy

当前可立即执行：

- G0：Codex active docs review。
- G1：Antigravity Controller Minimum State Machine。
- G2：G1 通过后进入 Fake OpenCode Runtime。

G3-G11 报告必须先存在为 pending，后续每个 Phase 开始前由 Codex 展开。
