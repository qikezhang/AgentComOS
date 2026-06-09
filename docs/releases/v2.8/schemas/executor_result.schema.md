# Executor Result Schema

## Required fields

- `command_id`: string
- `policy_id`: string
- `adapter`: string
- `status`: enum: `completed`, `failed`, `blocked`, `timeout`, `requires_approval`
- `started_at`: timestamp or null
- `completed_at`: timestamp or null
- `exit_code`: integer or null
- `stdout_redacted`: string
- `stderr_redacted`: string
- `blocked_reason`: string or null
- `timeout_seconds`: integer
- `audit_id`: string

## Rule

Blocked or requires_approval results must never be reported as completed.
