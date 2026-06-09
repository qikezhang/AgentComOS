from typing import Optional, List
from dataclasses import dataclass, field, asdict

@dataclass
class SafetyInbound:
    token_present: bool = False
    secret_detected: bool = False
    command_auto_executed: bool = False
    shell_executed: bool = False
    manual_os_bypassed: bool = False
    decision_feynman_bypassed: bool = False

@dataclass
class DiscordInboundMessage:
    message_id: str
    channel_id: str
    author_id_hash: str
    received_at: str
    content_redacted: str
    attachments_count: int = 0
    phase: str = "G11_GM_DISCORD_CONTROLLED_BRIDGE"
    safety: SafetyInbound = field(default_factory=SafetyInbound)

    def model_dump(self):
        return asdict(self)

@dataclass
class SafetyOutbound:
    real_discord_send: bool = False
    token_used: bool = False

@dataclass
class DiscordOutboundMessage:
    message_id: str
    channel_id: str
    sent_at: str
    content: str
    reply_to_message_id: Optional[str] = None
    phase: str = "G11_GM_DISCORD_CONTROLLED_BRIDGE"
    safety: SafetyOutbound = field(default_factory=SafetyOutbound)

    def model_dump(self):
        return asdict(self)

@dataclass
class SafetyCommand:
    read_only: bool
    requires_explicit_confirmation: bool
    auto_execute: bool = False
    real_os_execution_allowed: bool = False
    shell_executed: bool = False
    token_redacted: bool = True

@dataclass
class GMCommand:
    command_id: str
    message_id: str
    run_id: str
    command_type: str
    requires_confirmation: bool
    risk_level: str
    safety: SafetyCommand
    source: str = "discord"
    status: str = "parsed"
    phase: str = "G11_GM_DISCORD_CONTROLLED_BRIDGE"

    def model_dump(self):
        return asdict(self)

@dataclass
class SafetyCommandResult:
    auto_execute: bool = False
    shell_executed: bool = False
    manual_os_bypassed: bool = False
    decision_feynman_bypassed: bool = False

@dataclass
class GMCommandResultArtifact:
    path: str

@dataclass
class GMCommandResult:
    command_id: str
    status: str
    summary: str
    artifacts: List[GMCommandResultArtifact] = field(default_factory=list)
    phase: str = "G11_GM_DISCORD_CONTROLLED_BRIDGE"
    safety: SafetyCommandResult = field(default_factory=SafetyCommandResult)

    def model_dump(self):
        return asdict(self)
