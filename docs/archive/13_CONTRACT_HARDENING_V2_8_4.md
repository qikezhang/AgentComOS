# Archived Reference: 13_CONTRACT_HARDENING_V2_8_4.md

> 中文备注：本文件是历史参考文档，不是当前活跃实施策略。当前活跃策略以 `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md`、`docs/17_PHASED_DELIVERY_PLAN.md`、`docs/18_ACCEPTANCE_GATES.md` 和 `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md` 为准。

# AgentComOS v2.8.5 工程契约加固说明

> 中文备注：v2.8.5 的目标不是扩大产品范围，而是把 v2.8 已确定的功能点变成能分阶段交付、审计和商业化部署准备的工程合同。

## 本轮新增

1. 跨文件契约校验器：`agentcomos validate` 不再只校验单个 schema，也检查任务、决策、Worker、Loop、Feynman 之间的一致性。
2. Docker tmux runtime 明确满足：`-it TTY`、容器常驻、安装 tmux、TERM/terminfo 正常。
3. 增加负例测试，确保错误设计会失败。
4. 增加数据驱动开发规范。
5. 增加 runtime profile 的中文说明和验收标准。

## 下一阶段优先级

P0：Controller 最小状态机、OpenCode Runtime Manager、tmux Worker Pool fake E2E。

P1：Decision Market 三档样例、Feynman 三段样例、Environment Probe、GM Discord 协议。

P2：Manual Release 闭环、Worker Evolution 闭环、GitTree/Auto Versioner enforcement。
