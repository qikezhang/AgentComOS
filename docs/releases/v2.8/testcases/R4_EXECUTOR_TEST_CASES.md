# R4 Executor Test Cases

## R4-EXE-001 Validate policy
Input: `templates/executor_policy.yaml`.  
Command: `agentcomos executor validate-policy --policy <file>`.  
Expected: valid.

## R4-EXE-002 Allowlisted command
Input: `testdata/executor_cases/allowlisted_docker_restart.yaml`.  
Expected: policy_result allowed, requires approval or explicit policy.

## R4-EXE-003 Block destructive command
Input: `blocked_rm_rf.yaml`.  
Expected: blocked, reason destructive_command_blocked.

## R4-EXE-004 Redaction
Input: command output containing token-like text.  
Expected: output redacted before artifact write.

## R4-EXE-005 Idempotency
Repeat same blocked command.  
Expected: no duplicate blocked events.

## R4-EXE-006 Executor disabled
Set executor disabled.  
Expected: all execution commands blocked with reason executor_disabled.
