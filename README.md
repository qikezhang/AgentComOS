# AgentComOS v2.8.6 Phase-Gated Controlled-to-Industrial Starter

AgentComOS 是 AI-native 公司的核心支撑平台。本包是 v2.8.6 工程契约版，目标是让 Codex / Antigravity 按分阶段、数据驱动、可验收的方式开发完整 v2.8 能力。

## v2.8.6 的关键调整

- 不删除 v2.8 的功能审计要点：GM、OpenCode、Controller、Hermes Worker、Core Worker Starter Pack、Decision Market、Feynman、Task Frontier、Loop、Manual OS、Worker Evolution、GitTree / Auto Versioner、Environment KB 都保留。
- 落地方式调整为三阶段治理：
  - `development_explicit`：开发初期 Decision Market / Feynman 默认不自动启用，需要用户或任务文件显式指定；高风险任务仍强制 gate。
  - `transition_assisted`：系统可以建议启用，但需要 GM / 用户 / 任务策略确认。
  - `industrial_auto`：工业化运行后，系统根据风险、不确定性、成本和策略自动判断是否启用。
- Controller 是第一优先级实现模块，必须先跑通状态机、事件日志、fake runtime 和恢复机制。
- Codex 负责项目管理、文档、schema、测试、审计和验收；Antigravity 负责代码开发、部署和运行维护。

## 本地验证

```bash
cp .env.example .env
make compile
make test
make validate-examples
```

当前基线验证：

```text
make compile: pass
make test: 44 passed
make validate-examples: Run validation passed
```

## Docker tmux runtime 验证

```bash
docker compose -f docker/docker-compose.runtime-tmux.yml up -d
docker compose -f docker/docker-compose.runtime-tmux.yml exec agentcomos-runtime bash -lc 'tmux -V && echo $TERM && tmux ls || true'
```

Docker tmux runtime 是可选 profile。MVP 推荐：Mac 本地 host runtime；Contabo 初期 host-systemd；业务项目用 Docker 部署。

## 关键中文文档入口

- `docs/00_PRODUCT_SPEC_V2_8.md`：完整 v2.8 产品方案基准 + v2.8.6 overlay。
- `docs/15_CODEX_ANTIGRAVITY_COLLABORATION.md`：Codex / Antigravity 协作合同。
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`：Controller 优先实现规格。
- `docs/17_PHASED_DELIVERY_PLAN.md`：分阶段交付计划。
- `docs/18_ACCEPTANCE_GATES.md`：阶段验收门槛。
- `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md`：Decision/Feynman 从显式到自动的采用策略。
- `docs/20_DATA_LEDGER_EVENT_MODEL.md`：数据驱动事件与指标模型。
- `docs/runbooks/docker-tmux-runtime.md`：Docker 中运行 tmux 的条件和用法。

## 首轮开发建议

1. Codex 先审查 `docs/15-20`、schemas、tests、examples 和 acceptance gates。
2. Antigravity 从 Phase 1 开始实现 Controller 最小状态机。
3. Phase 2 使用 fake OpenCode；Phase 4 使用 fake Hermes；之后再接真实 OpenCode / Hermes。

## v2.8.6 phase-gated controlled-to-industrial notes

中文备注：本 starter 包按 v2.8 完整方案保留全部长期目标，但开发落地采用分阶段策略。开发初期 Decision Market / Feynman 仅在用户显式指定、任务文件 required、或高风险强制 gate 时启用；过渡阶段由系统建议；工业化阶段再由系统自动判断。

当前 runtime 策略：Mac 与 Contabo MVP 以 host runtime / host-systemd 为主；业务项目用 Docker；docker-tmux-runtime 仅作为实验 profile。未来可演进为 Docker 负责安装与环境封装，Controller / OpenCode / Hermes / tmux 等服务由 systemd 等系统级服务启动。

开发优先级：Controller Minimum State Machine → Fake OpenCode → Real OpenCode → tmux Fake Hermes → Real Hermes → Evidence/Delivery/GM Report → Operating Program → Optional/Assisted Decision/Feynman → Loop → Manual/Worker Evolution/Auto Versioner。

## v2.8.6 Locked Next Steps

1. **Codex G0 Review**：执行 `codex/tasks/g0-active-docs-review.md`，确认活跃文档和历史文档边界，并更新 `codex/acceptance-reports/G0_CONTRACT_BASELINE.md`。
2. **Antigravity G1 Implementation**：执行 `antigravity/tasks/phase-1-implement-controller-state-machine.md`，只实现 Controller Minimum State Machine。
3. **Codex All Phase Reports**：Codex 必须维护 `codex/acceptance-reports/G0-G11` 全部验收报告；每个 Phase 开始前补齐细则，交付后执行验收。
4. **G1 Passed → G2 Fake OpenCode**：只有 G1 报告为 `passed` 后，才允许开始 `antigravity/tasks/phase-2-fake-opencode-runtime.md`。
