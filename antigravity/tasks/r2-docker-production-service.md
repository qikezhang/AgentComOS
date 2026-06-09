# 实现 R2 Docker Production Service

## Objective
Implement Docker / Docker Compose supervised production-like service for AgentComOS v2.8.

## Scope
- Dockerfile
- docker-compose.yml
- .env.example
- .dockerignore
- agentcomos healthcheck
- mounted runtime/logs/reports/backups volumes
- restart policy
- tests for Docker production contract
- R2 Antigravity task doc
- R2 Codex acceptance report, status pending

## Out of Scope
- Real Discord Bot
- Controlled Executor
- shell/ssh/sudo/docker/systemctl execution
- Operation Adapters
- G12+
- Worker Evolution
- Auto Versioner
- arbitrary command execution

## Implemented Files
- Dockerfile
- docker-compose.yml
- .env.example
- .dockerignore
- src/agentcomos/cli.py (healthcheck added)
- tests/test_r2_docker_production.py
- tests/test_r2_healthcheck.py
- tests/test_r2_release_hygiene.py
- antigravity/tasks/r2-docker-production-service.md
- codex/acceptance-reports/R2_DOCKER_PRODUCTION_SERVICE.md

## Test Plan
- Run `make test` to ensure basic checks and R2 targeted tests pass.
- Run `docker compose config` to statically validate compose file.
- Verify `agentcomos healthcheck` executes successfully.

## Safety Boundaries
- No real discord implementation.
- No executor or shell evaluation added.
- No secrets committed.

## Acceptance Criteria
- Dockerfile and compose file present and valid.
- Volumes mounted appropriately.
- Tests passing.
- Hygiene rules observed.

## Cleanup Notes
- Ensure `.agentcomos/runs` is clean before committing.
- Ensure `.env` is not tracked.
