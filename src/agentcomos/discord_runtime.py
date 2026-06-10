import asyncio
import logging
from pathlib import Path
from typing import Optional, Protocol, Dict, Any
import discord
from agentcomos.discord_config import load_discord_config
from agentcomos.discord_adapter import ingest_test
from agentcomos.discord_redaction import redact_string

logger = logging.getLogger(__name__)

class DiscordOutboundSender(Protocol):
    async def send(self, channel_id: str, content: str) -> None:
        ...

class RealDiscordOutboundSender:
    def __init__(self, client: discord.Client):
        self.client = client

    async def send(self, channel_id: str, content: str) -> None:
        channel = self.client.get_channel(int(channel_id))
        if not channel:
            try:
                channel = await self.client.fetch_channel(int(channel_id))
            except Exception as e:
                raise Exception(f"Channel not found or accessible: {e}")
                
        if channel:
            await channel.send(content)
        else:
            raise Exception("Channel not found")


class DiscordRuntime:
    def __init__(self, client: discord.Client, runtime_dir: Path):
        self.client = client
        self.runtime_dir = runtime_dir
        self.config = load_discord_config()
        
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def on_ready(self):
        logger.info(f"Discord adapter runtime started. Logged in as {self.client.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user or message.author.bot:
            return

        message_data = {
            "message_id": str(message.id),
            "guild_id": str(message.guild.id) if message.guild else "",
            "channel_id": str(message.channel.id),
            "author_id_hash": str(hash(message.author.id)),
            "roles": [str(role.id) for role in getattr(message.author, "roles", [])],
            "content": message.content
        }

        try:
            result = ingest_test(message_data, self.runtime_dir)
            
            # Real outbound handling
            from agentcomos.discord_artifacts import load_artifact, save_artifact, append_audit, DiscordAudit
            from datetime import datetime, timezone
            
            outbound_artifact = load_artifact(self.runtime_dir, "discord_outbound_message.yaml")
            
            if outbound_artifact and outbound_artifact.get("status") == "success":
                if not self.config.outbound_replies:
                    outbound_artifact["delivery_status"] = "skipped"
                    outbound_artifact["failure_reason"] = "outbound_disabled"
                    save_artifact(self.runtime_dir, "discord_outbound_message.yaml", outbound_artifact)
                    return

                sender = RealDiscordOutboundSender(self.client)
                try:
                    await sender.send(message_data["channel_id"], outbound_artifact["content_redacted"])
                    outbound_artifact["delivery_status"] = "sent"
                except Exception as e:
                    outbound_artifact["delivery_status"] = "failed"
                    outbound_artifact["failure_reason"] = redact_string(str(e))
                    
                    # Audit outbound failure
                    now_str = datetime.now(timezone.utc).isoformat()
                    audit = DiscordAudit(
                        timestamp=now_str,
                        inbound_message_id=message_data["message_id"],
                        duplicate=False,
                        permission_decision="unknown", # We append this just for the outbound failure record
                        permission_reason="outbound_failure",
                        command_type="unknown",
                        command_risk="unknown",
                        outbound_status="failed"
                    )
                    append_audit(self.runtime_dir, audit)
                    
                save_artifact(self.runtime_dir, "discord_outbound_message.yaml", outbound_artifact)
                        
        except Exception as e:
            logger.error(f"Error processing inbound message: {e}")

class DiscordClientFactory(Protocol):
    def create(self) -> discord.Client:
        ...

class RealDiscordClientFactory:
    def create(self) -> discord.Client:
        intents = discord.Intents.default()
        intents.message_content = True
        return discord.Client(intents=intents)

async def serve_discord(runtime_dir: Path, client_factory: Optional[DiscordClientFactory] = None) -> Dict[str, Any]:
    config = load_discord_config()
    
    if not config.enabled:
        return {"status": "unavailable", "reason": "disabled"}
        
    if not config.is_token_available():
        return {"status": "unavailable", "reason": "token_missing"}
        
    if client_factory is None:
        client_factory = RealDiscordClientFactory()
        
    client = client_factory.create()
    runtime = DiscordRuntime(client, runtime_dir)
    
    try:
        await client.start(config.token)
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Failed to start discord client: {e}")
        raise
