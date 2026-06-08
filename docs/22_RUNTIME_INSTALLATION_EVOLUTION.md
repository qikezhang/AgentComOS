# Runtime Installation Evolution Plan — v2.8.6

> 中文备注：当前开发阶段维持 host runtime + Docker 业务部署。未来可以演进为 Docker 负责安装和环境封装，相关服务以 systemd 等系统级方式启动。

## Current phase

```text
Mac dev: host runtime
Contabo MVP: host-systemd runtime
Business project: Docker compose
Docker tmux runtime: experimental
```

## Why not docker-tmux as production now

```text
TTY and interactive session complexity
container restart recovery
manual attach complexity
volume persistence
user permissions
Docker socket security
process supervision
```

## Future target

```text
Docker image builds and pins tool versions.
Bootstrap container or script installs Controller/OpenCode/Hermes/tmux.
Systemd manages long-running services.
Controller manages runtime state and tmux sessions.
Business apps deploy through Docker compose.
```

## Future services

```text
agentcomos-controller.service
agentcomos-opencode.service
agentcomos-gm-discord.service
agentcomos-health.timer
agentcomos-backup.timer
```

## Migration criteria

Only migrate after:

```text
host-systemd MVP stable for 30 days
backup/restore verified
rollback verified
observability verified
all credentials managed safely
Codex commercial audit passed
```
