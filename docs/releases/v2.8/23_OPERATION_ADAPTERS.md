# 23 Operation Adapters

## Shell Adapter

Allowed:
- allowlisted shell commands only
- timeout
- cwd lock
- environment redaction

Blocked:
- arbitrary bash
- destructive commands
- unrestricted env access

## SSH Adapter

Allowed:
- host allowlist
- user allowlist
- command allowlist
- timeout

Blocked:
- arbitrary ssh
- unknown host
- unrestricted remote shell

## Sudo Adapter

Allowed:
- least privilege
- command allowlist
- explicit policy

Blocked:
- arbitrary sudo
- unrestricted root shell

## Docker Adapter

Allowed examples:
- docker ps
- docker logs <service>
- docker compose ps
- docker compose logs <service>
- docker compose restart <allowlisted service>

Blocked examples:
- docker system prune
- docker compose down
- docker rm
- docker exec unrestricted shell

## Systemctl Adapter

Allowed examples:
- systemctl status <service>
- systemctl restart <allowlisted service>

Blocked examples:
- systemctl stop critical service
- systemctl disable
- arbitrary service names
