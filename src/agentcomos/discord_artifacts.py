import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class DiscordInboundMessage:
    message_id: str
    guild_id: str
    channel_id: str
    author_id_hash: str
    role_names_or_hashes: List[str]
    content_redacted: str
    received_at: str
    source: str = "discord"
    adapter_version: str = "v2.8-r3"
    duplicate_of: Optional[str] = None

@dataclass
class PermissionResult:
    permission_result_id: str
    message_id: str
    subject_user_hash: str
    guild_id: str
    channel_id: str
    roles: List[str]
    command_risk: str
    decision: str
    reason: str
    evaluated_at: str
    source: str = "discord"

@dataclass
class GMCommand:
    gm_command_id: str
    source_message_id: str
    command_type: str
    command_text_redacted: str
    risk_level: str
    requires_executor: bool
    requires_approval: bool
    status: str
    created_at: str
    blocked_reason: Optional[str] = None

@dataclass
class DiscordOutboundMessage:
    outbound_id: str
    source_message_id: str
    channel_id: str
    status: str
    content_redacted: str
    created_at: str
    delivery_status: str
    failure_reason: Optional[str] = None

@dataclass
class DiscordAudit:
    timestamp: str
    inbound_message_id: str
    duplicate: bool
    permission_decision: str
    permission_reason: str
    command_type: str
    command_risk: str
    outbound_status: str

def save_artifact(runtime_dir: Path, name: str, data: Any):
    """Save an artifact to the runtime directory."""
    runtime_dir.mkdir(parents=True, exist_ok=True)
    file_path = runtime_dir / name
    
    if hasattr(data, '__dataclass_fields__'):
        data_dict = asdict(data)
    elif isinstance(data, dict):
        data_dict = data
    else:
        raise ValueError("Data must be a dataclass or a dictionary")
        
    file_path.write_text(yaml.dump(data_dict, sort_keys=False), encoding="utf-8")

def load_artifact(runtime_dir: Path, name: str) -> Optional[Dict[str, Any]]:
    """Load an artifact from the runtime directory."""
    file_path = runtime_dir / name
    if not file_path.exists():
        return None
    return yaml.safe_load(file_path.read_text(encoding="utf-8"))

def append_audit(runtime_dir: Path, audit: DiscordAudit):
    """Append an audit entry to discord_audit.yaml."""
    runtime_dir.mkdir(parents=True, exist_ok=True)
    audit_file = runtime_dir / "discord_audit.yaml"
    
    audits = []
    if audit_file.exists():
        audits = yaml.safe_load(audit_file.read_text(encoding="utf-8")) or []
        
    audits.append(asdict(audit))
    audit_file.write_text(yaml.dump(audits, sort_keys=False), encoding="utf-8")
