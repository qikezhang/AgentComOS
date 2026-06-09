# 34 Discord Runtime Behavior

## Required runtime behavior

Real Discord Bot must implement or document:

- startup validation
- token missing behavior
- reconnect behavior
- rate limit behavior
- duplicate message idempotency
- outbound reply failure behavior
- offline recovery
- graceful shutdown
- audit on every inbound message
- redaction before logging

## Duplicate message handling

If a Discord message with the same message_id is received again:

- do not create duplicate GM command
- return or reference existing command
- append at most one idempotency event if needed

## Rate limit handling

If Discord rate limit occurs:

- do not drop audit
- record outbound failure or delay
- command execution result remains authoritative
- retry policy must be bounded

## Outbound failure

If outbound reply fails:

- command result remains valid
- outbound artifact status becomes failed
- GM Report discloses outbound failure
