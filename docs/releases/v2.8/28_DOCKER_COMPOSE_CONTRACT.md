# 28 Docker Compose Contract

## Required files

- Dockerfile
- docker-compose.yml
- .env.example
- docs/releases/v2.8/20_DOCKER_PRODUCTION_MODEL.md
- tests/test_r2_docker_production.py or equivalent

## Required service

Service name:

```text
agentcomos
```

## Required volumes

```text
./runtime/.agentcomos/runs:/app/.agentcomos/runs
./runtime/logs:/app/logs
./runtime/reports:/app/reports
./runtime/backups:/app/backups
```

## Required environment variables

- AGENTCOMOS_ENV
- AGENTCOMOS_RUNTIME_DIR
- AGENTCOMOS_LOG_DIR
- AGENTCOMOS_REPORT_DIR
- AGENTCOMOS_BACKUP_DIR

## Required healthcheck

Healthcheck must run a safe local command:

```text
agentcomos healthcheck
```

## Restart policy

Production profile must use:

```text
restart: unless-stopped
```

## Forbidden

- real `.env` committed
- secrets in compose
- runtime artifacts committed
- production container writing into git-tracked runtime paths
