# R2 Docker Test Cases

## R2-DOC-001 Dockerfile exists
Command: `test -f Dockerfile`.  
Expected: file exists.

## R2-DOC-002 Compose config validates
Command: `docker compose config`.  
Expected: passes without real secret values.

## R2-DOC-003 Healthcheck
Command: `agentcomos healthcheck`.  
Expected status: completed.  
Must not happen: writes runtime artifacts.

## R2-DOC-004 Runtime volume
Check compose mounts runtime directory outside git-tracked artifacts.

## R2-DOC-005 Secrets hygiene
Command: grep for token/password/private key.  
Expected: no real secret.
