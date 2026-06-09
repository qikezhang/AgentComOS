# 29 Real Discord Permission Contract

## Required permission checks

Real Discord Bot must enforce:

- guild allowlist
- channel allowlist
- user allowlist
- role allowlist
- command risk classification

## Command risk classes

- read_only
- controlled_write
- high_risk
- blocked

## Permission conflict rules

- deny overrides allow
- unknown defaults to block
- missing policy defaults to block
- high-risk requires explicit policy
- arbitrary command always blocked
- disabled executor blocks all execution commands
- disabled bot blocks all inbound processing except healthcheck/status

## Default behavior

Unknown command: blocked.  
Unknown user: blocked.  
Unknown channel: blocked.  
Missing token: service unavailable, not fallback to fake success.

## Token handling

Token must be read from deployment environment or secret manager only.

Forbidden:

- storing token in artifacts
- printing token
- logging token
- committing token
