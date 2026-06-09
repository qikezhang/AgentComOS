# 21 Real Discord Bot Adapter

## Target

R3 implements a real Discord Bot adapter for v2.8 final delivery.

## Current status

G11 is fake/mock adapter only.

## Token handling

Allowed:

- deployment `.env`
- Docker secret
- external secret manager

Forbidden:

- committing token to git
- logging token
- storing token in artifacts

## Permission model

Required:

- guild allowlist
- channel allowlist
- user allowlist
- role allowlist
- command risk classification
- read-only command default
- controlled command routing to executor
- deny-overrides-allow conflict resolution

## Runtime behavior

Required:

- reconnect behavior
- rate-limit safe behavior
- duplicate message idempotency
- outbound reply failure handling
- service unavailable when token missing

## Command path

```text
Discord Message
→ Inbound Artifact
→ Permission Check
→ GM Command
→ Controlled Executor
→ Result Artifact
→ Outbound Reply
→ Audit
```
