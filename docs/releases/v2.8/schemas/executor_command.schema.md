# Executor Command Schema

## Required fields

- `command_id`: string
- `source`: enum: `discord`, `cli`, `manual`
- `requested_by_hash`: string
- `adapter`: enum: `shell`, `ssh`, `sudo`, `docker`, `systemctl`
- `command_ref`: string
- `parameters`: map
- `risk_level`: enum: `low`, `medium`, `high`, `blocked`
- `requires_approval`: boolean
- `timeout_seconds`: integer
- `status`: enum: `requested`, `policy_checked`, `requires_approval`, `approved`, `executing`, `completed`, `failed`, `blocked`

## Forbidden

- unrestricted raw shell
- secret values
- private keys
