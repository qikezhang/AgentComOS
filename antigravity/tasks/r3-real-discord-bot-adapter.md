# R3 Real Discord Bot Adapter

Status: planned

## Goal

Implement the real Discord Bot adapter as the default enterprise interaction entry for AgentComOS v2.8, while preserving the strict non-bypass rule: Discord never directly executes system commands.

## Source of truth

- docs/releases/v2.8/phases/R3_REAL_DISCORD_BOT_ADAPTER_SPEC.md
- docs/releases/v2.8/21_REAL_DISCORD_BOT_ADAPTER.md
- docs/releases/v2.8/29_REAL_DISCORD_PERMISSION_CONTRACT.md
- docs/releases/v2.8/33_PERMISSION_RESOLUTION_RULES.md
- docs/releases/v2.8/34_DISCORD_RUNTIME_BEHAVIOR.md
- docs/releases/v2.8/testcases/R3_DISCORD_TEST_CASES.md
- docs/releases/v2.8/codex/R3_CODEX_REVIEW_CHECKLIST.md

## Scope

- Real Discord Bot adapter process integration.
- Token loading from deployment environment or secret manager.
- Missing token reports unavailable, never fake connected.
- Guild/channel/user/role allowlist.
- Permission result artifact.
- Discord inbound message artifact.
- Discord outbound reply artifact.
- Read-only command path.
- Duplicate message idempotency.
- Outbound reply failure handling.
- Audit for inbound/outbound events.
- Tests for R3 Discord behavior.

## Out of scope

- Controlled Executor implementation.
- shell/ssh/sudo/docker/systemctl operation adapters.
- Arbitrary command execution.
- Direct system command execution from Discord.
- docker.sock mount.
- privileged container.
- R4/R5/G12 work.

## Strict boundary

Discord adapter may create inbound artifacts, permission results, and GM commands. It must not directly execute shell, ssh, sudo, docker, or systemctl commands.

## Initial implementation checklist

- [ ] Add Discord config schema usage.
- [ ] Add token loading without logging or persisting token.
- [ ] Add status command for adapter availability.
- [ ] Add ingest-test path for deterministic tests.
- [ ] Add permission checks.
- [ ] Add permission_result artifact.
- [ ] Add inbound/outbound artifacts.
- [ ] Add duplicate message idempotency.
- [ ] Add tests.
- [ ] Add Codex acceptance report with Status: pending.

## Test checklist

- [ ] Missing token does not pass as connected.
- [ ] Token not written to logs/artifacts.
- [ ] Disallowed channel blocked.
- [ ] Disallowed user blocked.
- [ ] Denied role blocks even if user is allowed.
- [ ] Read-only status creates GM command.
- [ ] Duplicate message does not duplicate command.
- [ ] Secret request blocked.
- [ ] Discord adapter does not execute system commands.
