# 25 Production Smoke Test Plan

## Smoke targets

- Docker Compose starts service.
- Healthcheck passes.
- Real Discord Bot connects.
- Read-only status command works.
- Allowlisted docker logs command works.
- Allowlisted systemctl status works.
- Controlled service restart works.
- Arbitrary shell command is blocked.
- Secret request is blocked.
- Permission conflict is blocked using deny-overrides-allow.
- Incident response emergency disable path works.
- Backup/restore path works.
- Evidence/Delivery/GM Report generated.
- Runtime artifacts remain in mounted volume.
- No secrets committed.
