# Phase 4 — tmux Hermes Worker Pool Fake E2E

## Scope

Implement only the G4 tmux worker pool fake E2E.

G4 proves that Controller-owned worker orchestration can:

- read a Worker Invocation
- create a worker job artifact
- start a stable tmux session when tmux is available
- run the deterministic fake Hermes worker
- collect required worker outputs
- update `worker_job.yaml`
- append worker events
- update `timeline.yaml`
- remain recoverable, auditable, and idempotent

## Required fake runtime

G4 uses only the fake Hermes worker.

The fake worker must:

- read the Worker Invocation YAML
- write `DONE.md`
- write `result.yaml`
- write `reasoning_summary.md`
- write additional required placeholder outputs when the invocation requires them
- avoid network access
- avoid LLM calls
- avoid real Hermes

## Forbidden in G4

G4 must not:

- call real `hermes chat`
- connect to real Hermes
- enter G5 Real Hermes Worker Runtime
- implement Loop Execution
- implement Manual OS
- implement Worker Evolution
- implement Auto Versioner
- implement Decision Market executor
- implement Feynman executor
- lower G1/G2/G3 acceptance behavior

## Runtime profile

CI may use fake-no-tmux behavior or skip tmux-dependent E2E tests unless tmux is available.

Local Mac and Contabo host-systemd profiles may use real tmux to run the fake worker.

If tmux is unavailable:

- CLI must report unavailable clearly
- tests must not globally fail
- worker jobs must not be marked completed
- output collection must not pretend missing outputs exist

## Rollback note

Rollback removes the G4 worker CLI, fake Hermes worker script, worker runtime package, and G4 tests. It does not rewrite `.agentcomos/runs` operating history.

