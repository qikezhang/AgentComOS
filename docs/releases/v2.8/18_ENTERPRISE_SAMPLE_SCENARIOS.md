# 18 Enterprise Sample Scenarios

## Scenario 1: Read-only service status

Employee asks Discord:

```text
status service agentcomos-app
```

Expected:

- Real Discord Bot ingests message.
- GM command generated.
- Controlled Executor classifies read-only.
- Docker/Systemctl status adapter runs if allowed.
- Result returned and audited.

## Scenario 2: Controlled service restart

Employee asks Discord:

```text
restart service agentcomos-app
```

Expected:

- command requires executor policy
- service must be allowlisted
- timeout required
- audit required
- output redacted
- GM report includes result

## Scenario 3: Block arbitrary command

Employee asks:

```text
run shell rm -rf /
```

Expected:

- blocked
- reason: destructive_command_blocked
- no shell executed
- report includes blocked reason

## Scenario 4: Permission conflict

User is allowlisted but role is denied.

Expected:

- blocked
- reason: role_denied
- deny overrides allow
