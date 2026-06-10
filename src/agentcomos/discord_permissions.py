import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from agentcomos.discord_config import DiscordConfig
from agentcomos.discord_artifacts import PermissionResult

class PermissionEvaluator:
    def __init__(self, config: DiscordConfig):
        self.config = config

    def _generate_id(self) -> str:
        return f"pr_{uuid.uuid4().hex[:12]}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def evaluate(self, 
                 message_id: str, 
                 guild_id: str, 
                 channel_id: str, 
                 user_hash: str, 
                 roles: List[str], 
                 command_risk: str = "unknown") -> PermissionResult:
        
        pr_id = self._generate_id()
        now_str = self._now()

        def block(reason: str) -> PermissionResult:
            return PermissionResult(
                permission_result_id=pr_id,
                message_id=message_id,
                subject_user_hash=user_hash,
                guild_id=guild_id,
                channel_id=channel_id,
                roles=roles,
                command_risk=command_risk,
                decision="blocked",
                reason=reason,
                evaluated_at=now_str
            )

        def allow(reason: str) -> PermissionResult:
            return PermissionResult(
                permission_result_id=pr_id,
                message_id=message_id,
                subject_user_hash=user_hash,
                guild_id=guild_id,
                channel_id=channel_id,
                roles=roles,
                command_risk=command_risk,
                decision="allowed",
                reason=reason,
                evaluated_at=now_str
            )

        if not self.config.enabled:
            return block("bot_disabled")

        if not self.config.is_token_available():
            return block("token_missing")

        if self.config.guild_allowlist and guild_id not in self.config.guild_allowlist:
            return block("guild_not_allowed")

        if self.config.channel_allowlist and channel_id not in self.config.channel_allowlist:
            return block("channel_not_allowed")

        # user allowed?
        user_is_allowed = False
        if self.config.user_allowlist and user_hash in self.config.user_allowlist:
            user_is_allowed = True

        # role denied?
        if self.config.denied_role_allowlist:
            for role in roles:
                if role in self.config.denied_role_allowlist:
                    return block("role_denied")

        # required role allowed?
        role_is_allowed = False
        if self.config.role_allowlist:
            for role in roles:
                if role in self.config.role_allowlist:
                    role_is_allowed = True

        if not user_is_allowed and not role_is_allowed:
            if self.config.user_allowlist and not self.config.role_allowlist:
                return block("user_not_allowed")
            elif self.config.role_allowlist and not self.config.user_allowlist:
                return block("role_not_allowed")
            elif self.config.user_allowlist and self.config.role_allowlist:
                return block("user_not_allowed") # simple fallback

        # Risk classification checks
        if command_risk == "blocked" or command_risk == "unknown":
            return block("command_unknown")
        
        if command_risk == "secret_request":
            return block("secret_request_blocked")

        if command_risk == "arbitrary_command":
            return block("arbitrary_command_blocked")
            
        if command_risk == "read_only":
            return allow("allowed_read_only")
            
        if command_risk == "controlled_write" or command_risk == "high":
            return allow("allowed_controlled_command")

        # default block
        return block("policy_missing")
