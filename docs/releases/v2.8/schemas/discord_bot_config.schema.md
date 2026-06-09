# Discord Bot Config Schema

## Required fields

- `discord_bot.enabled`: boolean
- `discord_bot.token_source`: enum: `env`, `docker_secret`, `external_secret_manager`
- `discord_bot.token_env_name`: string
- `discord_bot.guild_allowlist`: list[string]
- `discord_bot.channel_allowlist`: list[string]
- `discord_bot.role_allowlist`: list[string]
- `discord_bot.user_allowlist`: list[string]
- `discord_bot.outbound_replies`: boolean
- `discord_bot.audit_all_messages`: boolean
- `discord_bot.default_command_mode`: enum: `read_only`, `controlled`
- `discord_bot.reconnect.enabled`: boolean
- `discord_bot.rate_limit.max_retries`: integer

## Forbidden

- literal token value
- password
- private key
