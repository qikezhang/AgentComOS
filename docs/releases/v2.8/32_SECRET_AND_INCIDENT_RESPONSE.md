# 32 Secret and Incident Response

## Token leakage response

If Discord token or any secret is suspected leaked:

1. Disable Discord Bot service.
2. Revoke or rotate token at provider.
3. Remove secret from deployment environment.
4. Inspect git history and runtime artifacts.
5. Generate incident report.
6. Re-enable service only after new token is injected securely.

## Emergency bot disable

Required command or runbook:

```text
docker compose stop agentcomos
```

or a documented feature flag:

```text
DISCORD_BOT_ENABLED=false
```

## Emergency executor disable

Required feature flag:

```text
CONTROLLED_EXECUTOR_ENABLED=false
```

When disabled, all execution commands must be blocked with reason:

```text
executor_disabled
```

## Incident report must include

- time
- detection source
- affected token or system
- immediate actions
- audit artifacts reviewed
- command history reviewed
- final status
- next prevention action
