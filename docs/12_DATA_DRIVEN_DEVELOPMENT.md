# AgentComOS v2.8.6 数据驱动开发规范

> 中文备注：本文件是开发执行的核心准则。所有模块都必须以数据协议、样例、负例测试和验收矩阵驱动，不能只凭自然语言描述实现。

## 1. 数据驱动开发原则

AgentComOS 的每一个运行阶段都必须产生可验证数据：

1. **输入数据**：Operating Intent、Daily Packet、Task Classification、Runtime Context。
2. **决策数据**：Decision Need Score、Decision Request、Proposal、Score、Critic、Synthesis、Final Decision。
3. **执行数据**：OpenCode Job、Worker Invocation、Worker Job、Loop Batch、tmux session registry。
4. **检查数据**：Feynman Result、Evidence Audit、Risk Audit、Release Judge Decision。
5. **学习数据**：Knowledge Card、Manual Update Proposal、Worker Evaluation、Failure Attribution、Ratchet Decision。
6. **版本数据**：Change Set、Version Record、Rollback Target。
7. **用户汇报数据**：Delivery Packet、User Report Packet。

## 2. 每个功能必须满足

- 有 schema。
- 有正例 example。
- 有负例 test。
- 有跨文件一致性校验。
- 有 Codex 审查任务。
- 有 Antigravity 实现任务。
- 有验收命令。

## 3. 禁止事项

- 禁止只写文档不写 schema。
- 禁止只有正例没有负例。
- 禁止 agent 猜环境事实。
- 禁止 Worker 绕过 OpenCode。
- 禁止 Controller 做认知判断。
- 禁止运营原始数据进入 GitTree 版本对象。

## 4. 关键验收命令

```bash
make compile
make test
make validate-examples
agentcomos validate examples/techai8/run/OI-TECHAI8-001
```
