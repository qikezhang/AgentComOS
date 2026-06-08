# Hermes tmux Worker Pool

Hermes Worker means a Hermes CLI process started inside tmux. Do not implement a custom worker daemon.

## Host-systemd profile
Recommended MVP. Controller, tmux, Hermes, and OpenCode run on host via systemd. Business projects deploy with Docker.

## Docker-tmux-runtime profile
Optional experiment. tmux, Hermes, OpenCode, and Controller run in one container. This simplifies isolation but complicates security, volumes, upgrades, and process supervision.

## Required checks
- tmux session exists
- output directory grows
- DONE.md appears
- failure_report.md handled
- stale sessions cleaned

## G4 fake E2E boundary

G4 may use tmux, but tmux must run only the deterministic fake Hermes worker. G4 does not call real Hermes, does not call an LLM, and does not implement G5.

Minimum G4 job identity:

```text
runtime: tmux_fake_hermes
fake_worker: true
real_hermes_used: false
tmux_session_name: agentcomos-<run_id>-<task_id>
```

If tmux is unavailable, the worker job must be recorded as unavailable or blocked and must not be marked completed.
