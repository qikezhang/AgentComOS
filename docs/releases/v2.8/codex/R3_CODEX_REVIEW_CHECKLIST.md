# R3 Codex Review Checklist

- [ ] Real Discord adapter implemented.
- [ ] Token loaded only from env/secret manager.
- [ ] Missing token does not report connected.
- [ ] Token never written to artifacts.
- [ ] Channel allowlist enforced.
- [ ] User allowlist enforced.
- [ ] Role allowlist enforced.
- [ ] Permission conflict uses deny-overrides-allow.
- [ ] Duplicate message idempotency passed.
- [ ] Read-only command produces GM command.
- [ ] Discord adapter does not execute shell/system command directly.
- [ ] Outbound reply audited.
- [ ] make compile/test/validate passed.
- [ ] No secrets committed.
