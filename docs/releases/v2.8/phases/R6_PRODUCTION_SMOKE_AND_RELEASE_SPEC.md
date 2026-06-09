# R6 Production Smoke and Release Spec

## Goal

Run final production-like smoke tests and prepare v2.8 release candidate.

## Scope

- VPS Docker Compose smoke
- Real Discord Bot smoke
- Controlled Executor smoke
- Operation Adapter smoke
- CI gate verification
- incident response smoke
- backup/restore smoke
- Evidence / Delivery / GM Report final validation
- release notes
- go/no-go checklist

## Acceptance criteria

- Docker service supervised and healthy
- Discord read-only command works
- controlled restart works
- arbitrary command blocked
- secret request blocked
- permission conflict blocked
- executor artifacts indexed
- incident response path validated
- backup/restore path validated
- no secrets committed
- Codex final review passed
