# Artifact Retention Policy Schema

## Required fields

- `policy_id`: string
- `logs_retention_days`: integer
- `run_artifacts_retention_days`: integer
- `gm_reports_retention_days`: integer
- `incident_reports_retention_days`: integer
- `backup_retention_days`: integer
- `backup_excludes`: list[string]
- `backup_includes`: list[string]

## Required exclusions

- `.env`
- raw tokens
- private keys
