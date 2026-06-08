# Codex / Antigravity Collaboration Contract — v2.8.6

> 中文备注：Codex 是契约、文档、审计和验收方；Antigravity 是代码实现、部署和运行维护方。两者必须通过 PR、测试和 evidence 协同，不能互相绕过。

## 1. 角色边界

### Codex owns

```text
docs/
schemas/
tests/
examples/
codex/tasks/
acceptance matrix
release manifest
review reports
commercial deployment audit
```

Codex 负责：

- 项目管理
- 文档更新维护
- schema 更新和一致性审查
- 正例 / 负例测试设计
- Codex review report
- Gate 验收
- Release manifest
- 商业化部署审计

Codex 不负责：

- 生产 runtime 代码实现
- 实际 VPS 部署操作
- 直接修改运行中实例
- 绕过 Antigravity 修复生产服务

### Antigravity owns

```text
src/
docker/
scripts/
antigravity/tasks/
deployment runbooks
runtime integrations
VPS operational instances
```

Antigravity 负责：

- Controller 实现
- OpenCode Runtime Manager 实现
- tmux Hermes Worker Pool 实现
- Docker / VPS 部署
- 运行实例维护
- 故障处理
- 日志和 metrics 接入
- evidence artifact 生成

Antigravity 不负责：

- 单方面修改产品边界
- 单方面降低验收标准
- 绕过 Codex 验收直接合并
- 未更新测试和 evidence 就声称完成

## 2. Shared ownership

以下文件必须双方 review：

```text
AGENTS.md
README.md
.agentcomos/policies/
.agentcomos/workers/specs/
.github/workflows/
pyproject.toml
Makefile
docker runtime profiles
```

## 3. Pull Request 要求

每个 PR 必须包含：

```text
1. 目标和阶段 Gate
2. 修改范围
3. Codex 影响
4. Antigravity 影响
5. 新增 / 更新测试
6. 新增 / 更新 examples
7. 验收命令输出
8. evidence artifact
9. 风险说明
10. rollback note
```

## 4. Codex Definition of Done

Codex 任务完成必须包含：

```text
文档更新
schema 更新
正例 example
负例 test
acceptance matrix 更新
release manifest 更新
review report
下一阶段阻塞项
```

## 5. Antigravity Definition of Done

Antigravity 任务完成必须包含：

```text
代码实现
单元测试
CLI / runtime 测试
fake E2E 或 real E2E
evidence artifact
runbook 更新
rollback note
不破坏 Codex 管理的契约边界
```

## 6. Merge Gate

合并前必须通过：

```bash
make compile
make test
make validate-examples
```

若涉及 runtime，还必须附加：

```text
runtime logs
events.jsonl
run_status.yaml
delivery_packet.yaml
user_report_packet.yaml
```

## 7. Dispute resolution

如果 Codex 和 Antigravity 对实现边界有冲突：

```text
1. 以 docs/00_PRODUCT_SPEC_V2_8.md 为产品基准。
2. 以 docs/17_PHASED_DELIVERY_PLAN.md 为实施顺序基准。
3. 以 docs/18_ACCEPTANCE_GATES.md 为验收基准。
4. 以用户 / Founder 的最新决策为最终裁决。
```
