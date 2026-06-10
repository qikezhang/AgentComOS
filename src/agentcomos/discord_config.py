import os
from typing import Dict, Any, List
from agentcomos.discord_redaction import redact_string

class DiscordConfig:
    def __init__(self):
        self.enabled: bool = os.environ.get("DISCORD_BOT_ENABLED", "false").lower() == "true"
        
        # Token is only loaded from env and strictly not logged
        self.token: str = os.environ.get("DISCORD_BOT_TOKEN", "")
        self.token_source: str = os.environ.get("DISCORD_BOT_TOKEN_SOURCE", "env")
        
        # Allowlists
        self.guild_allowlist: List[str] = self._parse_list(os.environ.get("DISCORD_GUILD_ALLOWLIST", ""))
        self.channel_allowlist: List[str] = self._parse_list(os.environ.get("DISCORD_CHANNEL_ALLOWLIST", ""))
        self.user_allowlist: List[str] = self._parse_list(os.environ.get("DISCORD_USER_ALLOWLIST", ""))
        self.role_allowlist: List[str] = self._parse_list(os.environ.get("DISCORD_ROLE_ALLOWLIST", ""))
        self.denied_role_allowlist: List[str] = self._parse_list(os.environ.get("DISCORD_DENIED_ROLE_ALLOWLIST", ""))
        
        self.outbound_replies: bool = os.environ.get("DISCORD_OUTBOUND_REPLIES", "true").lower() == "true"
        self.audit_all_messages: bool = os.environ.get("DISCORD_AUDIT_ALL_MESSAGES", "true").lower() == "true"
        self.default_command_mode: str = os.environ.get("DISCORD_DEFAULT_COMMAND_MODE", "controlled")

    def _parse_list(self, val: str) -> List[str]:
        if not val:
            return []
        return [item.strip() for item in val.split(",") if item.strip()]

    def is_token_available(self) -> bool:
        if not self.token:
            return False
        if "replace-with" in self.token or "PLACEHOLDER" in self.token:
            return False
        return True

    def dump_safe(self) -> Dict[str, Any]:
        """Returns a safe configuration dictionary with the token redacted."""
        return {
            "enabled": self.enabled,
            "token_source": self.token_source,
            "token": "***REDACTED***" if self.token else None,
            "token_available": self.is_token_available(),
            "guild_allowlist": self.guild_allowlist,
            "channel_allowlist": self.channel_allowlist,
            "user_allowlist": self.user_allowlist,
            "role_allowlist": self.role_allowlist,
            "denied_role_allowlist": self.denied_role_allowlist,
            "outbound_replies": self.outbound_replies,
            "audit_all_messages": self.audit_all_messages,
            "default_command_mode": self.default_command_mode,
        }

def load_discord_config() -> DiscordConfig:
    return DiscordConfig()
