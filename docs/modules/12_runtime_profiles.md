# Runtime Profiles

## host-systemd recommended MVP
- Controller: systemd service
- OpenCode: host process managed by Controller/systemd
- Hermes Worker: host tmux + hermes CLI
- Business app: Docker Compose

## docker-tmux-runtime optional
- Controller, tmux, Hermes, and OpenCode in one runtime container
- Requires mounted workspace and persistent state/log volumes
- Not recommended until host-systemd MVP is stable
