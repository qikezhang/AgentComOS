# 22 Controlled Executor Framework

## Core principles

- No arbitrary execution.
- All execution is policy checked.
- All execution is auditable.
- All execution is bounded.
- All execution has timeout.
- All output is redacted.
- All risky execution has approval or explicit policy.

## Supported executor types

- shell
- ssh
- sudo
- docker
- systemctl

## Lifecycle

```text
requested
→ parsed
→ permission_checked
→ policy_checked
→ previewed
→ approved
→ executing
→ completed / failed / blocked
→ rolled_back if applicable
```

## Artifacts

- executor_policy.yaml
- executor_command.yaml
- executor_result.yaml
- executor_audit.md
- permission_result.yaml
