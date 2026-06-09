# R1 G11 Merge and Main Stabilization Spec

## Goal

Merge completed G11 into main and establish a stable baseline for R2-R8.

## Scope

- G11 quick re-review passed.
- G11 branch merged to main.
- main validation passed.
- no runtime artifacts committed.
- no secrets committed.
- release baseline documented.

## Out of scope

- Docker production work.
- Real Discord Bot.
- Controlled Executor.
- Operation Adapters.

## Required checks

- `git checkout main`
- `git pull origin main`
- merge G11 with no file-scope pollution
- `make compile`
- `make test`
- `make validate-examples`
- no `.agentcomos/runs`
- no `uv.lock` unless explicitly allowed
- no `.env`
- no secrets

## Acceptance criteria

- G11 acceptance report passed.
- main is clean.
- R2 may start from latest main.
