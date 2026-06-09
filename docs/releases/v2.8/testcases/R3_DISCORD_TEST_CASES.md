# R3 Discord Test Cases

## R3-DIS-001 Missing token
Input: no token environment.  
Command: `agentcomos discord status`.  
Expected status: unavailable.  
Must not happen: fake connected success.

## R3-DIS-002 Token redaction
Input: deployment token via env.  
Expected: token not written to logs/artifacts.

## R3-DIS-003 Disallowed channel
Input: message from unknown channel.  
Expected status: blocked.  
Reason: channel_not_allowed.

## R3-DIS-004 Read-only status
Input: `testdata/discord_real_adapter_cases/read_only_status_message.yaml`.  
Expected: GM command generated.  
Must not happen: system command directly executed by Discord adapter.

## R3-DIS-005 Block secret request
Input: `blocked_secret_request.yaml`.  
Expected: blocked, secret_disclosed=false.

## R3-DIS-006 Duplicate message idempotency
Input: same message_id twice.  
Expected: no duplicate command execution.

## R3-DIS-007 Permission conflict
Input: user allowed, role denied.  
Expected: blocked, reason role_denied.
