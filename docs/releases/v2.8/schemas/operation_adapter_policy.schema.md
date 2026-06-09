# Operation Adapter Policy Schema

## Required sections

- `shell`
- `ssh`
- `sudo`
- `docker`
- `systemctl`

## Required safety switches

- `allow_arbitrary_shell`: false
- `allow_arbitrary_ssh`: false
- `allow_arbitrary_sudo`: false
- `allow_arbitrary_docker`: false
- `allow_arbitrary_systemctl`: false

## Required allowlists

- ssh host allowlist
- docker service allowlist
- systemctl service allowlist
- command allowlist
