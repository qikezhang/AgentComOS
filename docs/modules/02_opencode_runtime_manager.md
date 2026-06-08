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

## Runtime Job Routing

OpenCode job routing is governed by `docs/27_RUNTIME_JOB_ROUTING_RULES.md`.

Field classes:

```text
Routing fields:
- runtime
- attempted_real_opencode
- future: attempted_real_hermes
- future: worker_runtime

Execution result fields:
- real_opencode_used
- real_hermes_used
- fake_runtime

Status fields:
- status
- failure_reason
- blocked_reason
- unavailable_reason
```

`collect`, `status`, and `recover` must choose the OpenCode handler from routing fields, not from execution result fields.

Required OpenCode routing:

```text
runtime: fake_opencode -> fake OpenCode handler
runtime: real_opencode -> real OpenCode handler
attempted_real_opencode: true -> real OpenCode handler
```

`real_opencode_used: false` means real OpenCode did not successfully execute. It does not mean the job is fake.

Forbidden:

```python
if real_opencode_used == True:
    route_real()
else:
    route_fake()
```

Required:

```python
if runtime == "real_opencode" or attempted_real_opencode == True:
    route_real()
elif runtime == "fake_opencode" or fake_runtime == True:
    route_fake()
else:
    fail_safely()
```

Unknown runtime identity must fail safely and must not default to fake.
