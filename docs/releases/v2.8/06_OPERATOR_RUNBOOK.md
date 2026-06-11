# 06 Operator Runbook

## Current G11 operator flow

1. Create an operating intent.
2. Build program.
3. Build frontier.
4. Use fake Discord message to create GM command.
5. Parse command.
6. Execute command with explicit confirmation where required.
7. Generate audit.
8. Generate Evidence / Delivery / GM Report.

## v2.8 final operator flow

1. Operator sends a Discord command.
2. Real Discord Bot ingests message.
3. GM command is generated.
4. Controlled Executor classifies risk.
5. Read-only commands may execute directly if allowed.
6. High-risk commands require approval or policy-approved automation.
7. Execution result is written as artifact.
8. GM Report and Discord reply summarize outcome.

## Operator safety rule

Do not attempt to use Discord as a raw shell. All operations must be expressed as controlled requests.

## Deployment Steps
Deployment instructions.

## Smoke Test
Run smoke test.

## Incident Response and Troubleshooting
How to handle incidents.

## Environment Variables
Set environment variables carefully.
