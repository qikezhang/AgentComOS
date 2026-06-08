# AgentComOS v2.8.6 Phase-Gated Controlled-to-Industrial Starter Release Manifest

> 中文备注：本发布包是 **AgentComOS v2.8.6 Phase-Gated Controlled-to-Industrial Starter**。它不是生产实现，而是用于驱动 Codex / Antigravity 分阶段开发、测试、审计和最终商业化部署准备的工程契约包。

## 1. 版本定位

v2.8.6 的定位是：

```text
Controlled Delivery first, Industrial Automation later.
先可控交付，再工业化自动运行。
```

本版继承 v2.8 的完整产品目标，但把落地策略调整为：

1. **Controller-first**：Controller 状态机、事件日志、幂等和恢复是第一优先级。
2. **Fake-runtime-first**：先用 fake OpenCode / fake Hermes 跑通闭环，再接真实 OpenCode / Hermes。
3. **Evidence-first**：每个阶段都必须产出可验证文件、日志和报告。
4. **Codex-gated delivery**：Codex 负责契约、文档、测试、审计和验收；Antigravity 负责实现、部署和运营实例。
5. **Decision / Feynman 三阶段采用**：开发初期显式启用，过渡期系统建议，工业化期策略自动判断。

## 2. 与 v2.8 完整方案的关系

v2.8 的完整目标不删除、不降级，包括：

- GM Hermes
- OpenCode Runtime
- Controller
- Hermes Worker via tmux
- Core Worker Starter Pack
- Decision Market
- Feynman Engine
- Task Frontier
- Loop Execution Engine
- Manual OS
- Worker Evolution
- GitTree / Auto Versioner
- Environment KB
- Operating Program
- Evidence Packet
- User Report Packet
- GM 汇报机制

v2.8.6 做的是 **落地顺序和启用门槛调整**：

```text
开发初期：Decision Market / Feynman 默认不自动扩散，用户显式指定或高风险任务才启用。
过渡阶段：系统可以建议启用，但需 GM / 用户 / 策略确认。
工业化阶段：系统根据风险、不确定性、成本、历史质量自动判断是否启用。
```

## 3. 本版相对上一版的关键修复

本版重点修复审查中发现的问题：

- 清除 v2.8.4 残留表述，统一为 v2.8.6。
- 将 “Decision/Feynman default flow” 修正为 “Explicit → Assisted → Industrial Auto”。
- 强化 Controller 实施规格，明确 Phase 1 最小状态机。
- 扩展 G0-G11 验收矩阵，便于 Codex 分阶段审计。
- 补充 Codex / Antigravity 协作合同、PR 模板和审计模板。
- 明确 tmux + Docker 当前开发阶段维持现有方式：host runtime 为主，docker-tmux-runtime 为实验 profile。
- 明确未来升级方向：Docker 负责安装和环境封装，Controller/OpenCode/Hermes/tmux 等服务以 systemd 等系统级方式启动。
- 增加商业化部署准备清单。

## 4. 当前 runtime 策略

### 当前开发阶段

```text
Mac 本地开发：host runtime
Contabo MVP：host-systemd runtime
业务项目部署：Docker
Docker tmux runtime：实验 profile，仅用于隔离测试
```

### 未来升级方向

```text
Docker 负责安装、打包、环境一致性和 bootstrap。
Controller / OpenCode / Hermes / tmux 等 runtime 服务由 systemd 或等价系统服务托管。
业务项目继续用 Docker / Docker Compose 发布。
```

这避免早期把 tmux 强行塞进生产容器导致 session 恢复、TTY、人工 attach、权限和进程管理复杂度失控。

## 5. 验证命令

每个 PR / 阶段验收至少运行：

```bash
make compile
make test
make validate-examples
```

商业化部署前还必须补充：

```text
runtime E2E evidence
backup / restore rehearsal
rollback rehearsal
secrets audit
cost / budget ledger
GM approval flow evidence
production healthcheck evidence
```

## 6. 发布包不应包含

以下文件不应进入 starter 包：

```text
.pytest_cache/
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.env
runtime logs
secrets
production data
```

## 7. 下一阶段建议

v2.8.6 之后的第一开发目标不是扩展功能，而是实现：

```text
Phase 1: Controller Minimum State Machine
Phase 2: Fake OpenCode Runtime
Phase 3: Real OpenCode Runtime Manager
Phase 4: tmux Hermes Worker Pool Fake E2E
```

只有这些稳定后，再进入真实 Hermes、Loop、Manual、Worker Evolution、Auto Versioner 和工业化自动治理。

## 8. 当前验证结果

```text
make compile: pass
make test: 44 passed
make validate-examples: Run validation passed
```

## 9. v2.8.6 Ordered Next Steps

本版将下一步执行顺序锁定为：

```text
1. Codex G0：执行 active docs review，确认活跃文档 / 历史文档边界。
2. Antigravity G1：实现 Controller Minimum State Machine。
3. Codex all Phase：维护并执行 G0-G11 全部 Phase Acceptance Reports。
4. G1 passed 后进入 G2：Antigravity 实现 Fake OpenCode Runtime。
```

新增入口：

```text
docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md
docs/25_PHASE_ACCEPTANCE_REPORTING.md
docs/26_G1_TO_G2_HANDOFF.md
codex/tasks/g0-active-docs-review.md
codex/tasks/all-phase-acceptance-reporting.md
antigravity/tasks/phase-2-fake-opencode-runtime.md
codex/acceptance-reports/G0-G11_*.md
```

Codex 必须为 all Phase 维护验收报告；Antigravity 不得跳过 G1 直接进入真实 OpenCode / Hermes 集成。
