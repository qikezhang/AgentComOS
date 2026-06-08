# Docker tmux Runtime Runbook

> 中文备注：docker-tmux-runtime 是可选运行模式。MVP 推荐 host-systemd；docker-tmux-runtime 用于隔离测试或后续生产化。

## 必须满足

根据项目约束，Docker 下运行 tmux 必须满足：

```text
-it TTY
容器常驻
安装 tmux
TERM/terminfo 正常
```

本项目通过以下方式满足：

- `docker-compose.runtime-tmux.yml` 设置 `tty: true` 和 `stdin_open: true`，等价于 `docker run -it` 的 TTY 条件。
- 容器 command 使用 `bash -lc "tmux start-server; tail -f /dev/null"`，保持容器常驻。
- `Dockerfile.runtime-tmux` 安装 `tmux` 和 `ncurses-term`。
- `ENV TERM=xterm-256color`，并安装 terminfo，保证终端能力正常。

## 手动 attach

```bash
docker compose -f docker/docker-compose.runtime-tmux.yml exec agentcomos-runtime bash
tmux ls
tmux attach -t <session>
```

## 生产建议

- 初期 Contabo 推荐 host-systemd：Controller/OpenCode/Hermes/tmux 跑宿主机，业务项目用 Docker。
- docker-tmux-runtime 生产化前必须补 healthcheck、supervisor、非 root 用户、持久化 state/log/workspace、backup/restore。
