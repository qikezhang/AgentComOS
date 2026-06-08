# Codex Task — All Phase Acceptance Reporting

> 中文备注：Codex 负责所有 Phase 的验收报告，不仅是 G0/G1。每个 Gate 开始前补齐验收细则，结束时执行验收并写结论。

## Goal

Maintain and execute G0-G11 acceptance reports.

## Report Directory

```text
codex/acceptance-reports/
```

## Required Reports

- `G0_CONTRACT_BASELINE.md`
- `G1_CONTROLLER_MINIMUM_STATE_MACHINE.md`
- `G2_FAKE_OPENCODE_RUNTIME.md`
- `G3_REAL_OPENCODE_RUNTIME_MANAGER.md`
- `G4_TMUX_HERMES_WORKER_POOL_FAKE_E2E.md`
- `G5_REAL_HERMES_WORKER_RUNTIME.md`
- `G6_EVIDENCE_DELIVERY_GM_REPORT.md`
- `G7_SIMPLE_OPERATING_PROGRAM.md`
- `G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION.md`
- `G9_LOOP_EXECUTION_TASK_FRONTIER.md`
- `G10_MANUAL_WORKER_EVOLUTION_AUTO_VERSIONER.md`
- `G11_INDUSTRIAL_AUTO_GOVERNANCE.md`

## Codex Responsibilities

For each gate:

1. Expand test criteria before implementation starts.
2. Ensure positive and negative tests exist.
3. Review Antigravity implementation evidence.
4. Execute required commands.
5. Update report status.
6. Block next gate if required evidence is missing.

## Definition of Done

A gate is complete only when its report status is `passed` and next gate unlock conditions are explicitly satisfied.
