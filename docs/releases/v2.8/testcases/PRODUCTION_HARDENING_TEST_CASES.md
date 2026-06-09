# Production Hardening Test Cases

## HARD-001 CI gates
Expected: compile/test/validate/secret scan/artifact scan pass.

## HARD-002 Token rotation
Simulate token rotation.  
Expected: old token removed, new token injected via environment, no token logged.

## HARD-003 Emergency bot disable
Set bot disabled.  
Expected: inbound processing blocked except status/healthcheck.

## HARD-004 Emergency executor disable
Set executor disabled.  
Expected: all execution commands blocked with reason executor_disabled.

## HARD-005 Permission precedence
Allowed user + denied role.  
Expected: blocked.

## HARD-006 Retention policy
Check retention policy exists and excludes `.env`, tokens, private keys.

## HARD-007 Backup excludes secrets
Backup artifact must not contain `.env` or token-like strings.
