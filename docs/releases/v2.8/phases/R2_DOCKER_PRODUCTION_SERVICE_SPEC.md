# R2 Docker Production Service Spec

## Goal

Implement Docker / Docker Compose supervised production-like service for AgentComOS v2.8.

## Scope

- Dockerfile
- docker-compose.yml
- .env.example
- healthcheck CLI
- mounted runtime/logs/reports/backups volumes
- restart policy
- production smoke command
- Docker documentation updates

## Out of scope

- real Discord Bot
- Controlled Executor
- shell/ssh/sudo/docker/systemctl execution
- G12+ features

## Required CLI

- `agentcomos healthcheck`
- optional: `agentcomos service status`

## Required tests

- compose config validates
- Dockerfile exists
- .env.example exists
- healthcheck command exists
- runtime volume paths are not git-tracked runtime artifacts
- no secrets in compose/env example

## Acceptance criteria

- make compile passed
- make test passed
- make validate-examples passed
- Docker build passed or compose config passed
- healthcheck passed
- no .env committed
- no runtime artifacts committed
