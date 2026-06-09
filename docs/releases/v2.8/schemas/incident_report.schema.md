# Incident Report Schema

## Required fields

- `incident_id`: string
- `detected_at`: timestamp
- `detected_by`: string
- `incident_type`: enum: `token_leak`, `unauthorized_command`, `executor_misfire`, `artifact_leak`, `other`
- `severity`: enum: `low`, `medium`, `high`, `critical`
- `immediate_actions`: list[string]
- `systems_disabled`: list[string]
- `tokens_rotated`: boolean
- `artifacts_reviewed`: list[string]
- `commands_reviewed`: list[string]
- `final_status`: enum: `open`, `contained`, `resolved`
- `prevention_actions`: list[string]
