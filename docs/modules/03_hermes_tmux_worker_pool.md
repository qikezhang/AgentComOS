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
