# R4 Controlled Executor Framework Spec

## Goal

Implement the central Controlled Executor that all risky operations must pass through.

## Scope

- executor policy loading
- permission result consumption
- executor command validation
- command_ref resolution
- risk classification
- approval requirement
- timeout enforcement
- redaction
- result artifacts
- audit artifacts
- Evidence / Delivery / GM Report integration
- executor disable switch

## Out of scope

- real adapter execution for shell/ssh/sudo/docker/systemctl may be mocked in R4
- arbitrary raw command execution

## Required CLI

- `agentcomos executor validate-policy --policy <file>`
- `agentcomos executor submit --command <file>`
- `agentcomos executor status --command-id <id>`
- `agentcomos executor run --command-id <id> --confirm explicit`
- `agentcomos executor audit --run <run_id>`

## Acceptance criteria

- allowlisted command passes policy
- arbitrary command blocked
- timeout required
- redaction applied
- executor disabled blocks execution
- repeated execute idempotent
- blocked command not reported completed
