# Phase 5: Real Hermes Worker Runtime

## Objectives
- Implement real Hermes worker runtime for Phase 5.
- Add `agentcomos worker start --invocation <file> --real`
- Maintain fake Hermes worker functionality.
- Correctly route jobs based on `runtime` and `attempted_real_hermes`.
- Write tests to verify availability check, missing binary handling, and routing logic.

## Steps
- [x] Read G5 specifications and G4 implementation (Loop 1).
- [x] Design real Hermes runtime manager (Loop 2).
- [x] Implement availability check / command builder / unavailable job logic (Loop 3).
- [x] Implement real worker start/status/collect/recover min path (Loop 4).
- [x] Add tests and negative cases (Loop 5).
- [x] Run full regression tests (Loop 6).
- [x] Clean artifacts and review boundaries (Loop 7).
- [x] Submit PR (Loop 8).
