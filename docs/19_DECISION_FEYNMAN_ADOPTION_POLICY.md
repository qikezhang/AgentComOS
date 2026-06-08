# Decision Market / Feynman Adoption Policy

> 中文备注：本策略修正 v2.8 的“默认启用”落地方式。完整 v2.8 的功能审计要点不删除；v2.8.6 采用分阶段启用：开发初期显式指定，成熟后自动判断。

## 1. 三阶段启用模型

### development_explicit
开发初期。默认不自动启用 Decision Market / Feynman。

启用条件：

- 用户显式说“启用抽卡/多方案比较/Decision Market”
- 用户显式说“启用费曼/对抗检查/Feynman”
- 任务文件写 `required: true`
- 高风险任务强制启用 release gate

### transition_assisted
过渡期。系统可以根据 Task Classification 和 Decision Need Score 给出建议，但需要 GM/用户或任务策略确认。

### industrial_auto
工业化期。系统根据策略自动判断是否启用，增强长期运营稳定能力。

## 2. Decision Market 自动判断条件（工业化期）

工业化期自动启用条件：

- `decision_need_score >= 20`
- 存在多方案路径或策略选择
- 存在 worker/manual/product/release 选择
- 用户可见影响为 medium 以上
- release/high-risk policy 强制

## 3. Feynman 自动判断条件（工业化期）

工业化期自动启用条件：

- 非极简单任务且 risk_level >= medium
- release/deployment/security/payment/legal/GM system/manual high-priority
- loop batch 进入下一批前
- evidence 缺口或前一次验收失败

## 4. 开发期强制禁止自动扩散

在 `development_explicit` 阶段，系统不得仅因不确定性自动拉起完整 Decision Market 或 Feynman。必须有显式触发或高风险强制。

## 5. 成本与预算

每次启用必须记录：

- reason
- trigger
- mode
- expected cost
- max proposals / reviewers / workers
- result artifact
