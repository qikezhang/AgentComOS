# Permission Result Schema

## Required fields

- `permission_result_id`: string
- `source`: enum: `discord`, `cli`, `manual`
- `subject_user_hash`: string
- `channel_id`: string or null
- `roles`: list[string]
- `command_risk`: enum: `read_only`, `controlled_write`, `high_risk`, `blocked`
- `decision`: enum: `allowed`, `blocked`
- `reason`: string
- `evaluated_at`: timestamp

## Required reasons

- bot_disabled
- executor_disabled
- token_missing
- guild_not_allowed
- channel_not_allowed
- user_not_allowed
- role_denied
- command_unknown
- policy_missing
- command_not_allowlisted
- arbitrary_command_blocked
