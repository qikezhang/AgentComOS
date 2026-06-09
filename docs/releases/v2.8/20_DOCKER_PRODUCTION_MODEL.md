# 20 Docker Production Model

## Decision

AgentComOS v2.8 final delivery uses Docker Compose as the default enterprise production deployment model.

## Requirements

- Dockerfile
- docker-compose.yml
- healthcheck
- restart policy
- runtime volume
- logs volume
- reports volume
- .env.example
- no real .env committed
- no secrets committed

## Runtime volumes

Recommended mounts:

```text
.agentcomos/runs -> /app/.agentcomos/runs
logs -> /app/logs
reports -> /app/reports
backups -> /app/backups
```

## Supervised service

The container may run a supervised service process after R2. The service must expose health status and logs.

## Emergency stop

A production deployment must document:

- stop Docker Compose
- disable Discord bot
- disable Controlled Executor
- collect evidence
- generate incident report
