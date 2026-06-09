# 10. GM / Discord Controlled Bridge (Phase G11)

## Overview
The GM / Discord Controlled Bridge allows users to interact with the GM via Discord. To maintain safety boundaries, this bridge operates exclusively using a fake/mock adapter. 

## Boundaries
- No real Discord connection.
- No real Discord token used or committed.
- No real OS commands (shell, ssh, sudo, systemctl, docker).
- No automatic bypass of G8 Decision/Feynman or G10 Manual OS explicit approvals.
- No Auto Versioner or Worker Evolution capabilities.

## Event Timeline
- `gm_discord.message.ingested`
- `gm_discord.command.parsed`
- `gm_discord.command.requires_confirmation`
- `gm_discord.command.executed`
- `gm_discord.command.blocked`
- `gm_discord.reply.prepared`
- `gm_discord.audit.generated`

## Artifacts
- `discord_inbound_message.yaml`
- `discord_outbound_message.yaml`
- `gm_command.yaml`
- `gm_command_result.yaml`
- `gm_discord_audit.md`
