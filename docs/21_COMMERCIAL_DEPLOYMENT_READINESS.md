# Commercial Deployment Readiness Checklist — v2.8.6

> 中文备注：本文件定义 Codex 审计商业化部署版本时的最低标准。当前 v2.8.6 starter 不声称已满足商业化部署，只提供未来验收标准。

## 1. Runtime stability

必须证明：

```text
Controller systemd service running
OpenCode runtime healthcheck
Hermes/tmux worker lifecycle tested
recover after restart
no orphan critical jobs
```

## 2. Evidence and auditability

必须提供：

```text
events.jsonl
run_status.yaml
opencode_job.yaml
worker_job.yaml
evidence_packet
delivery_packet
user_report_packet
release_decision
rollback_target
```

## 3. Security and secrets

必须满足：

```text
.env 不入 Git
secrets runbook
credential_request flow
approval_request flow
no secrets in logs
no secrets in evidence packet
```

## 4. Backup / restore

必须演练：

```text
state backup
workspace backup
manual backup
version ledger backup
restore to new VPS
```

## 5. Rollback

必须证明：

```text
project release rollback
manual rollback
worker spec rollback
controller config rollback
```

## 6. Cost and budget

必须有：

```text
cost_usage_record
worker budget
loop budget
decision/feynman budget
alert threshold
```

## 7. GM approval flow

必须有：

```text
approval_request.yaml
credential_request.yaml
gm_message.yaml
user response linkage
blocked until approval semantics
```

## 8. Runtime profile

MVP 生产建议：

```text
host-systemd runtime
business app Docker deployment
docker-tmux-runtime experimental only
```

## 9. Codex commercial audit report

Codex 必须输出：

```text
docs/reports/commercial_audit_<date>.md
```

报告模板见：

```text
docs/templates/codex_commercial_audit_report.md
```
