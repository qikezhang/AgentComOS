# 17 Antigravity Execution Guide

Antigravity must use this documentation pack to implement future phases.

## Execution rule

Do not implement R3 before R2 is merged.  
Do not implement R4 before R3 is merged.  
Do not implement R5 before R4 is merged.  
Do not proceed to R7 before R6 release readiness passes.

## Branch plan

- R1: `release/r1-g11-main-stabilization`
- R2: `antigravity/r2-docker-production-service`
- R3: `antigravity/r3-real-discord-bot-adapter`
- R4: `antigravity/r4-controlled-executor-framework`
- R5: `antigravity/r5-operation-adapters`
- R6: `ops/v2.8-production-smoke-test`
- R7: `release/v2.8.0-rc1`
- R8: `release/v2.8.0-final`

## Safety rule

No direct execution from Discord. Discord creates GM command only.
