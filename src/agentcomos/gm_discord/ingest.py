import os
import yaml
import hashlib
from datetime import datetime, timezone
from agentcomos.gm_discord.models import DiscordInboundMessage, SafetyInbound
from agentcomos.controller.events import append_event
from agentcomos.controller.state import get_run_dir

def ingest_message(run_id: str, message_file: str, is_fake: bool) -> str:
    if not is_fake:
        raise ValueError("Only fake adapter is allowed for G11 ingest")
    
    with open(message_file, 'r') as f:
        data = yaml.safe_load(f)
    
    content = data.get("content", "")
    content_redacted = _redact_secrets(content)
    
    author_id_hash = data.get("author_id_hash")
    if not author_id_hash and "author_id" in data:
        author_id_hash = hashlib.sha256(data["author_id"].encode()).hexdigest()
    
    inbound = DiscordInboundMessage(
        message_id=data.get("message_id", "MSG-UNKNOWN"),
        channel_id=data.get("channel_id", "UNKNOWN"),
        author_id_hash=author_id_hash or "anonymous",
        received_at=datetime.now(timezone.utc).isoformat(),
        content_redacted=content_redacted,
        attachments_count=data.get("attachments_count", 0),
        safety=SafetyInbound(
            token_present=False,
            secret_detected=(content != content_redacted),
        )
    )
    
    run_dir = get_run_dir(run_id)
    artifact_path = run_dir / "gm_discord" / "inbound" / f"{inbound.message_id}.yaml"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(artifact_path, 'w') as f:
        yaml.safe_dump(inbound.model_dump(), f, sort_keys=False)
        
    append_event(run_id, "gm_discord.message.ingested", {
        "message_id": inbound.message_id,
        "path": str(artifact_path.relative_to(run_dir.parent.parent))
    })
    
    return str(artifact_path)

def _redact_secrets(content: str) -> str:
    redacted = content
    secrets = ["token", "password", "secret", "DISCORD_TOKEN", "BOT_TOKEN"]
    if any(s in redacted.lower() for s in secrets):
        return "<REDACTED>"
    return redacted
