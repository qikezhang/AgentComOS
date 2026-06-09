# R3 Real Discord Bot Adapter Spec

## Goal

Implement real Discord Bot adapter as the default enterprise interaction entry.

## Scope

- Discord bot process integration
- token loading from environment or secret manager
- guild/channel/user/role allowlist
- permission result artifact
- inbound message artifact
- outbound reply artifact
- read-only command path
- audit
- duplicate message idempotency
- service unavailable behavior when token missing
- no direct system execution

## Out of scope

- Controlled Executor execution
- shell/ssh/sudo/docker/systemctl adapters
- arbitrary command execution

## Required CLI

- `agentcomos discord status`
- `agentcomos discord run --dry-run` or equivalent supervised service entry
- `agentcomos discord ingest-test` for test mode

## Required artifacts

- permission_result.yaml
- discord_inbound_message.yaml
- discord_outbound_message.yaml
- discord_adapter_status.yaml
- discord_audit.md

## Acceptance criteria

- missing token does not pass as connected
- token never written to artifacts
- disallowed channel blocked
- disallowed user blocked
- disallowed role blocked
- permission conflict resolved by deny-overrides-allow
- read-only command generates GM command
- no system command executed by Discord adapter
