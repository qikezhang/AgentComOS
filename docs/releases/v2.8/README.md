# AgentComOS v2.8 Enterprise Delivery Final Execution Pack

This package is the execution-level documentation set for finishing AgentComOS v2.8 enterprise delivery.

It includes:

- current G0-G11 capability baseline
- v2.8 final production target
- R1-R8 delivery phases
- Docker production model
- Real Discord Bot adapter requirements
- Controlled Executor requirements
- shell / ssh / sudo / docker / systemctl operation adapter contracts
- schemas
- test cases
- Codex review checklists
- production hardening contracts
- incident response
- CI/release gates
- artifact retention / backup / restore policy

## v2.8 final target

AgentComOS v2.8 final delivery target is:

1. Docker / Docker Compose supervised production operation.
2. Real Discord Bot as the default enterprise interaction entry.
3. Controlled automatic execution for:
   - shell
   - ssh
   - sudo
   - docker
   - systemctl
4. All execution must go through the Controlled Executor:
   - command allowlist
   - user / role / channel permission
   - explicit policy check
   - timeout
   - audit log
   - output redaction
   - rollback note where applicable
   - Evidence / Delivery / GM Report integration

## Current status distinction

Current G11 status:

- fake/mock GM Discord Controlled Bridge
- no real Discord connection
- no shell/ssh/sudo/docker/systemctl execution
- protocol foundation only

v2.8 final delivery target:

- supervised Docker service
- real Discord adapter
- controlled executor
- operation adapters

## Execution phases

- R1: G11 Merge and Main Stabilization
- R2: Docker Production Service
- R3: Real Discord Bot Adapter
- R4: Controlled Executor Framework
- R5: Operation Adapters
- R6: Production Smoke and Release Readiness
- R7: v2.8.0 Release Candidate
- R8: v2.8.0 Final Release

## Non-bypass rule

Discord must never directly execute system commands. Discord creates a GM command. GM command enters Controlled Executor. Controlled Executor applies policy. Operation Adapter executes only approved and allowlisted commands.
