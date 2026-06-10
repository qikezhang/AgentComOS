# R4 Controlled Executor Framework Implementation Task

**目标**
实现受控执行器框架（Controlled Executor Framework），允许 AgentComOS 将来自 Discord / GM / CLI 的 controlled command request 转换为一个可审计、可拒绝、可批准、可排队、可模拟执行的 decision/result。仅包含框架，不包含实际的 shell/ssh/sudo/docker adapter。

## 任务列表
- [x] Create Executor config and models (`executor_config.py`, `executor_request.py`, `executor_decision.py`, `executor_result.py`)
- [x] Implement Executor classifier (`executor_classifier.py`)
- [x] Implement Executor policy engine (`executor_policy.py`)
- [x] Implement Executor framework processing logic (`executor_framework.py`)
- [x] Implement Executor CLI commands (`status`, `evaluate`, `run-dry`)
- [x] Integrate R3 Discord GM commands to generate Executor Requests
- [x] Create and run R4 unit tests
- [x] Create R4 Acceptance Report
