# 35 Artifact Retention, Backup, and Restore

## Runtime artifact categories

- `.agentcomos/runs`
- executor artifacts
- Discord inbound/outbound artifacts
- GM reports
- delivery packets
- evidence packets
- logs
- backups

## Git rule

Runtime artifacts must not be committed.

## Retention policy

Default pilot recommendation:

- logs: 14 days
- run artifacts: 30 days
- GM reports: 90 days
- incident reports: 180 days
- backups: operator-defined

## Backup

Backup must include:

- runtime runs
- reports
- executor audit
- configuration templates without secrets

Backup must exclude:

- `.env`
- raw tokens
- private keys

## Restore smoke

Restore smoke should prove:

- selected run can be restored
- GM report can be read
- evidence packet can be read
- no secret appears in restored artifacts
