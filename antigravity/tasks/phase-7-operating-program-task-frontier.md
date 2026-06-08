# Phase 7 — Operating Program / Task Frontier

## Goal

Implement a controller-owned Operating Program and Task Frontier for run `OI-TECHAI8-001`.

## Required CLI

- `agentcomos program build --run <run_id>`
- `agentcomos program status --run <run_id>`
- `agentcomos frontier build --run <run_id>`
- `agentcomos frontier status --run <run_id>`
- `agentcomos frontier list --run <run_id>`
- `agentcomos frontier next --run <run_id>`
- `agentcomos frontier update --run <run_id> --task <task_id> --status <status>`
- `agentcomos controller tick --run <run_id> --fake`

## Acceptance

- Program build uses `operating_intent.yaml` and fails safely when objective is missing.
- Frontier build creates the three required G7 tasks.
- Dependency resolution blocks dependent tasks until prerequisites complete.
- Controller tick advances at most one ready task.
- Fake OpenCode, fake Hermes, and reporting tasks stay on fake/controller paths.
- Evidence, delivery, and GM report include G7 artifacts.
- G1-G6 regressions continue to pass.

## Rollback

Remove G7 program/frontier modules, CLI commands, tests, and docs. Do not rewrite `.agentcomos/runs` history.

