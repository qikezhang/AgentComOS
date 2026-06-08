# Archived Reference: 11_ENGINEERING_CONTRACT_V2_8_3.md

> 中文备注：本文件是历史参考文档，不是当前活跃实施策略。当前活跃策略以 `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md`、`docs/17_PHASED_DELIVERY_PLAN.md`、`docs/18_ACCEPTANCE_GATES.md` 和 `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md` 为准。

# AgentComOS v2.8.3 Engineering Contract

This pass converts the v2.8 product plan into enforceable engineering contracts.

## Development rule
No production feature is accepted unless it has: schema, positive example, negative test when applicable, CLI or state-machine check, evidence artifact, and acceptance gate.

## Immediate P0 gates
- Python source compiles.
- `agentcomos --help` works.
- `agentcomos validate examples/techai8/run/OI-TECHAI8-001` passes.
- Worker Invocation cannot be created by GM.
- Non-trivial tasks require Decision/Feynman artifacts.
