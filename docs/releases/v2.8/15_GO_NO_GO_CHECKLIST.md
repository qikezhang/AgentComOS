# 15 Go / No-Go Checklist

## Main readiness

- [ ] G11 merged to main
- [ ] main make compile passed
- [ ] main make test passed
- [ ] main make validate-examples passed

## Docker production

- [ ] Docker Compose production profile exists
- [ ] Docker healthcheck exists
- [ ] Docker restart policy exists
- [ ] Runtime volume configured
- [ ] Logs volume configured
- [ ] Reports volume configured
- [ ] .env.example exists
- [ ] no real .env committed

## Real Discord

- [ ] Real Discord Bot adapter passed smoke
- [ ] Discord token not committed
- [ ] Channel allowlist enforced
- [ ] User allowlist enforced
- [ ] Role allowlist enforced
- [ ] Permission conflict rules enforced
- [ ] Outbound reply audited

## Controlled Executor

- [ ] Controlled Executor policy exists
- [ ] Shell adapter allowlist enforced
- [ ] SSH adapter allowlist enforced
- [ ] Sudo adapter allowlist enforced
- [ ] Docker adapter allowlist enforced
- [ ] Systemctl adapter allowlist enforced
- [ ] Arbitrary command execution blocked
- [ ] Executor timeout enforced
- [ ] Executor output redaction enforced
- [ ] Executor audit generated
- [ ] Evidence/Delivery/GM Report include executor artifacts

## Production hardening

- [ ] CI release gate exists
- [ ] Secret scan gate exists
- [ ] Artifact pollution gate exists
- [ ] Token rotation playbook exists
- [ ] Emergency bot disable playbook exists
- [ ] Emergency executor disable playbook exists
- [ ] Backup/restore smoke passed
- [ ] Retention policy documented

## Release

- [ ] VPS production smoke passed
- [ ] Known limitations reviewed
- [ ] Codex final release review passed
- [ ] v2.8.0-rc1 tag created
- [ ] v2.8.0 final tag created
