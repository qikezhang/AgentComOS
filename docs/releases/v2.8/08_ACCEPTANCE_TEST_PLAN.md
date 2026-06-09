# 08 Acceptance Test Plan

## Core validation

- make compile
- make test
- make validate-examples
- G1-G11 regression
- no runtime artifacts committed
- no uv.lock committed unless explicitly allowed
- no .env committed
- no real secrets committed

## v2.8 final validation additions

- Docker Compose service starts.
- Docker healthcheck passes.
- Docker restart policy works.
- Runtime volume works.
- Logs volume works.
- Real Discord Bot connects using deployment secret.
- Discord channel allowlist enforced.
- Discord user/role allowlist enforced.
- Permission conflict resolution enforced.
- Controlled Executor policy enforced.
- Shell adapter allowlist enforced.
- SSH adapter allowlist enforced.
- Sudo adapter allowlist enforced.
- Docker adapter allowlist enforced.
- Systemctl adapter allowlist enforced.
- Arbitrary command execution blocked.
- Secret request blocked.
- Incident response smoke passed.
- Backup/restore smoke passed.
- Evidence/Delivery/GM Report include executor artifacts.
