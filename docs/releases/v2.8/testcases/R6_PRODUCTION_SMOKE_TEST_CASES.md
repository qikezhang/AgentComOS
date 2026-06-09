# R6 Production Smoke Test Cases

## R6-SMK-001 Start compose
Command: `docker compose up -d`.  
Expected: service running.

## R6-SMK-002 Healthcheck
Command: `docker compose ps` and healthcheck.  
Expected: healthy.

## R6-SMK-003 Discord status command
Send allowed read-only command.  
Expected: reply, audit, GM command.

## R6-SMK-004 Controlled restart
Send allowlisted restart command.  
Expected: executor result, audit, report.

## R6-SMK-005 Arbitrary command blocked
Send `run shell rm -rf /`.  
Expected: blocked and reported.

## R6-SMK-006 Final report
Run Evidence / Delivery / GM Report.  
Expected: executor artifacts indexed.

## R6-SMK-007 Incident response
Disable bot and executor via documented controls.  
Expected: inbound/execution blocked with clear reasons.

## R6-SMK-008 Backup restore
Backup and restore a selected run.  
Expected: report/evidence readable after restore.
