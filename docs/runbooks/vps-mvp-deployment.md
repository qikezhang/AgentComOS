# VPS MVP Docker Deployment & Testing Runbook

由于目标 VPS 上已经存在正在运行的 Hermes 服务，为避免环境冲突，我们采用 **`docker-tmux-runtime`** 的方案在隔离的容器内进行 AgentComOS 的初次实体运行与端到端测试。

## 1. 准备代码库与环境变量

在 VPS 上克隆或上传代码后，进入项目根目录：

```bash
cd /opt/AgentComOS
```

由于要启动真实的 Hermes Worker，你需要提供真实的大模型 API 密钥。复制样例并创建真正的 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，**必须配置的项**包括：
```env
AGENTCOMOS_ENV=production
AGENTCOMOS_TIMEZONE=America/Los_Angeles

# Token (至少填一个你打算用的模型)
OPENAI_API_KEY=sk-xxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxx
```

## 2. 启动 Docker 容器环境

在项目根目录下，使用 `docker compose` 拉起预置好的 `runtime-tmux` 环境容器：

```bash
cd docker/
docker compose -f docker-compose.runtime-tmux.yml up -d --build
```

拉起后，该容器 (`agentcomos-runtime`) 会在后台挂载您的代码库和独立的 tmux Server。它会自动读取代码根目录的 `.env` 文件。

## 3. 测试用例执行

为验证 Controller -> OpenCode -> Hermes -> tmux 容器内链路，我们使用预先准备好的意图。我们需要**进入到容器中**执行命令：

### 3.1 提交测试意图
```bash
docker compose -f docker-compose.runtime-tmux.yml exec agentcomos-runtime bash
# 现在你在容器内了！工作目录应为 /workspace
agentcomos run create --intent examples/vps-mvp-test/operating_intent.yaml
```
记录下生成的 `run_id`。

### 3.2 触发事件循环
既然在容器内，你可以直接手动触发 Controller 派发任务：
```bash
agentcomos controller tick --run <run_id>
```

### 3.3 验证 Worker 在容器内的执行
当 tick 完成，任务被发给 tmux 内的 Hermes 后，通过以下命令围观：
```bash
# 列出容器内的 tmux session
tmux ls

# attach 到该 session 观看 Hermes 的写代码过程
tmux attach-session -t <session_name>
```

*(按 `Ctrl+B` 然后按 `d` 可以从 tmux 回话中 detach 出来，不中断任务)*

### 3.4 收集执行结果
当 AI 任务完成：
```bash
agentcomos worker collect --job <worker_job_id>
```

## 4. 结束与清理
离开容器，你可以随时停止并删除这个隔离的测试环境：
```bash
exit
docker compose -f docker-compose.runtime-tmux.yml down
```
