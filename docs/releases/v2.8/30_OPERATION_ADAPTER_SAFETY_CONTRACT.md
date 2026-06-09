# 30 Operation Adapter Safety Contract

## Shell

- no arbitrary shell
- no destructive commands
- command_ref required
- cwd lock required
- timeout required

## SSH

- host allowlist required
- user allowlist required
- command_ref required
- no interactive session
- timeout required

## Sudo

- no arbitrary sudo
- explicit command allowlist
- least privilege required
- timeout required

## Docker

- service allowlist required for service operations
- destructive docker commands blocked by default
- docker exec unrestricted shell blocked

## Systemctl

- service allowlist required
- allowed actions explicit
- stop/disable blocked by default unless explicitly allowed in policy

## Reporting

All adapter results must be included in Evidence / Delivery / GM Report.
