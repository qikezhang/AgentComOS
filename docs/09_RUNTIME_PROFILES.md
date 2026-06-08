# AgentComOS v2.8.6 Runtime Profiles

> 中文备注：本文件明确开发期、MVP 部署期和未来工业化部署期的 runtime 策略。当前阶段 **维持现有方式**：host runtime 为主，docker-tmux-runtime 只作为实验 profile。未来再考虑 Docker 负责安装，相关服务以系统级方式启动。

## 1. 当前推荐策略

### Mac 本地开发

```text
Controller: host process
OpenCode: host process / opencode serve
Hermes Worker: host tmux + hermes CLI
Business app: Docker Compose if needed
```

原因：

- 调试简单。
- tmux attach 方便。
- OpenCode / Hermes 版本和环境问题容易定位。
- 不把 Docker、tmux、LLM runtime 的问题混在一起。

### Contabo MVP 部署

```text
Controller: systemd service on host
OpenCode: host process managed by systemd / Controller
Hermes Worker: host tmux + hermes CLI
Business app: Docker / Docker Compose
```

原因：

- tmux 天然适合 host session。
- systemd 适合监管长期服务。
- 业务应用仍可 Docker 化发布。
- 早期避免 docker-in-docker / tmux-in-container 的进程和 TTY 复杂度。

## 2. docker-tmux-runtime：实验 profile

Docker 内运行 tmux 必须满足：

```text
-it / TTY
容器常驻
安装 tmux
TERM / terminfo 正常
workspace / state / logs volume 持久化
```

当前开发包保留：

```text
docker/Dockerfile.runtime-tmux
docker/docker-compose.runtime-tmux.yml
docs/runbooks/docker-tmux-runtime.md
```

但该 profile 只用于隔离测试，不作为第一生产路径。

## 3. 未来升级方向

未来可以升级为：

```text
Docker 负责安装、打包、bootstrap、版本固定和环境一致性。
Controller / OpenCode / Hermes / tmux 以 systemd 或等价系统服务启动。
业务应用继续 Docker 化部署。
```

也就是：

```text
Docker = installation and packaging layer
systemd = long-running service supervision layer
tmux = Hermes Worker interactive session layer
Controller = runtime state machine and scheduler
```

## 4. 不推荐的早期路径

早期不推荐：

```text
Controller + OpenCode + Hermes + tmux 全部塞进生产容器
容器内再控制宿主机 Docker
容器重启后仍假设 tmux session 自动保留
无 volume / 无 healthcheck / 无 attach runbook 就生产化 docker-tmux-runtime
```

## 5. Runtime Profile Gate

任何 runtime profile 进入生产前必须通过：

```text
1. healthcheck
2. restart recovery
3. log persistence
4. state persistence
5. backup / restore
6. manual attach / debug runbook
7. secret handling
8. rollback plan
9. cost / resource budget
10. Codex commercial deployment audit
```
