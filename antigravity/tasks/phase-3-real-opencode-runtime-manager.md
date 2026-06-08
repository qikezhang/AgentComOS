# Phase 3 - Real OpenCode Runtime Manager

**Goal:** Implement G3 Real OpenCode Runtime Manager while maintaining G2 fake runtime integrity and preventing any execution of Hermes, tmux, Loop, or Manual OS features.

## Requirements

1. **Real OpenCode CLI Actions:** Add support for `agentcomos opencode start`, `serve`, `status`, `submit --real`, `collect`, `recover`, `stop`.
2. **Fake/Real Separation:** Default tests and CI use `--fake`. `--real` is strictly opt-in.
3. **Availability Checks:** Determine if `opencode` binary exists and report its status clearly without failing the test suite or fake runs.
4. **Command Building:** Formulate proper startup (`serve`) and job execution (`run --attach`) commands for OpenCode.
5. **Runtime Ledgers:** Update and write to `opencode_runtime_status.yaml` capturing `real_opencode` execution intent.
6. **Job Status Update:** In cases where OpenCode isn't installed locally, generate an `unavailable` or `blocked` job, never pretending completion.
7. **Event Emitting:** Fire proper real OpenCode events: `opencode.runtime.checked`, `opencode.runtime.available`, `opencode.real.job.created`, etc.
8. **Strict Boundaries:** NO hermes, NO tmux session creation, NO worker evolution.

## Acceptance Tests Needed

- missing binary correctly reports `unavailable`/`blocked` instead of completing
- fake paths are not influenced
- tests pass without depending on the actual binary being present

This file serves as the tracking documentation for the G3 Phase tasks.
