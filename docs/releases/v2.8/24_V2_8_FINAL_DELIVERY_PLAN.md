# 24 v2.8 Final Delivery Plan

## Required sequence

1. R1 G11 merge and main stabilization
2. R2 Docker Production Service
3. R3 Real Discord Bot Adapter
4. R4 Controlled Executor Framework
5. R5 Operation Adapters
6. R6 Enterprise Delivery Docs + VPS Production Smoke
7. R7 v2.8.0-rc1
8. R8 v2.8.0 Final Release

## Release criteria

v2.8 final cannot be released until:

- Docker production smoke passes.
- Real Discord smoke passes.
- Controlled Executor smoke passes.
- shell/ssh/sudo/docker/systemctl adapters enforce allowlists.
- arbitrary command execution is blocked.
- CI/release gates pass.
- incident response smoke passes.
- backup/restore smoke passes.
- Evidence/Delivery/GM Report include executor artifacts.
- Codex final review passes.
