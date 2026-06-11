# 05 Deployment Runbook

## Default delivery mode

AgentComOS v2.8 final delivery uses Docker Compose as the default enterprise deployment mode.

Local Python/venv remains supported for development and debugging.

## Deployment modes

1. Development mode
   - local Python/venv
   - make compile
   - make test
   - make validate-examples

2. Production-like mode
   - Dockerfile
   - docker-compose.yml
   - mounted runtime volume
   - mounted logs volume
   - mounted reports volume
   - healthcheck
   - restart policy

3. Enterprise pilot mode
   - VPS
   - Docker Compose
   - Real Discord Bot
   - Controlled Executor
   - Evidence / Delivery / GM Report archival

## Runtime artifact rule

`.agentcomos/runs` is runtime data. It may be mounted as a volume but must not be committed.

## Secret rule

`.env` and real secrets are deployment-only. They must not be committed.

## Operational runbook minimum

A production-like deployment must include:

- start
- stop
- restart
- healthcheck
- logs
- backup
- restore
- token rotation
- emergency disable bot
- emergency disable executor

## Rollback Plan
If failure occurs, perform rollback.

### Trigger conditions
Trigger on failure.

### Steps
1. Revert changes.
