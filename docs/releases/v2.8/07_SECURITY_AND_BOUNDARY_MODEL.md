# 07 Security and Boundary Model

## v2.8 final security model

v2.8 final delivery permits controlled automatic execution, but never arbitrary execution.

## Required controls

- command allowlist
- user allowlist
- role allowlist
- channel allowlist
- timeout
- working directory constraints
- host allowlist for ssh
- service allowlist for systemctl
- docker service allowlist
- output redaction
- audit artifacts
- Evidence / Delivery / GM Report integration
- rollback note where applicable
- deny-overrides-allow permission resolution
- incident response playbooks

## Prohibited

- arbitrary command execution
- unrestricted bash
- unrestricted ssh
- unrestricted sudo
- uncontrolled root access
- token committed to git
- no-audit production execution
- unbounded loop
- Discord message directly executing shell

## Risk table

| Risk | Control | Residual Risk | Future hardening |
|---|---|---|---|
| Discord token leak | secret manager / .env only | token misuse | rotation policy |
| prompt injection | allowlist and parser | social engineering | permission hardening |
| destructive command | denylist + allowlist | policy misconfig | dry run and approval |
| infinite loop | max_ticks | bad configuration | central policy |
| sudo abuse | command allowlist | privilege escalation | least privilege sudoers |
| artifact growth | retention policy | disk pressure | external storage |
