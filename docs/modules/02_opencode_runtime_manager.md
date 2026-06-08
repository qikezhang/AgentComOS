# OpenCode Runtime Manager

OpenCode is the persistent engineering runtime. Controller starts `opencode serve` and submits jobs through `opencode run --attach`.

## Required ledgers
- opencode_job.yaml
- opencode_session_ledger.yaml
- opencode_runtime_status.yaml

## Rules
- Plan sessions are fresh.
- Build may fork/continue from Plan.
- Review and Judge sessions are fresh.
- Session exports are evidence.
