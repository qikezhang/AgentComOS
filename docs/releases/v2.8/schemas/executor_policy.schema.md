# Executor Policy Schema

## Required fields

- `policy_id`: string
- `version`: integer
- `default_action`: enum: `block`, `allow_read_only`
- `allowed_sources`: list[string]
- `allowed_channels`: list[string]
- `allowed_roles`: list[string]
- `allowed_users`: list[string]
- `adapters`: map
- `redaction_patterns`: list[string]

## Adapter policy fields

Each adapter may include:

- `enabled`: boolean
- `allowed_commands`: list
- `timeout_seconds`: integer
- `allowed_hosts`: list
- `allowed_services`: list
- `allowed_actions`: list

## Validation rules

- `default_action` should be `block` for production.
- all executable commands must have command id and template.
- timeout must be present for executable commands.
