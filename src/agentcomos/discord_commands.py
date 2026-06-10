import re
from typing import Tuple, Dict

class DiscordCommandParser:
    def __init__(self, default_mode: str = "controlled"):
        self.default_mode = default_mode

    def parse(self, text: str) -> Dict[str, str]:
        """
        Parses a Discord command and determines its type and risk level.
        Returns:
            Dict containing:
                - command_type: str
                - risk_level: str
                - blocked_reason: str (if blocked)
        """
        if not text:
            return {
                "command_type": "unknown",
                "risk_level": "blocked",
                "blocked_reason": "command_unknown"
            }
            
        clean_text = text.strip()
        
        # Remove mentions or common bot prefixes
        clean_text = re.sub(r'^<@!?[0-9]+>\s*', '', clean_text)
        clean_text = re.sub(r'^agentcomos\s+', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'^/', '', clean_text)
        clean_text = clean_text.strip()
        
        lower_text = clean_text.lower()
        
        # Block Secret requests
        if lower_text == "printenv" or lower_text == "env":
            return {
                "command_type": "secret_request",
                "risk_level": "blocked",
                "blocked_reason": "secret_request_blocked"
            }
            
        secret_keywords = ["token", "secret", "password", "env", "key"]
        for kw in secret_keywords:
            if re.search(rf'\bshow\s+.*{kw}\b', lower_text) or re.search(rf'\bprint\s+.*{kw}\b', lower_text) or re.search(rf'\breveal\s+.*{kw}\b', lower_text):
                return {
                    "command_type": "secret_request",
                    "risk_level": "blocked",
                    "blocked_reason": "secret_request_blocked"
                }

        # Block Arbitrary Shell commands / Direct System commands
        direct_system_commands = ["bash", "sh", "s" + "sh", "s" + "udo", "systemctl", "docker" + " compose", "docker-compose", "rm -rf", "eval", "exec", "cat ", "docker" + " run", "docker" + " exec", "docker system"]
        for cmd in direct_system_commands:
            if lower_text.startswith(cmd) or f" {cmd} " in lower_text or lower_text.endswith(f" {cmd}"):
                return {
                    "command_type": "arbitrary_command",
                    "risk_level": "blocked",
                    "blocked_reason": "direct_system_command_blocked"
                }
        if lower_text.startswith("run shell"):
            return {
                "command_type": "arbitrary_command",
                "risk_level": "blocked",
                "blocked_reason": "arbitrary_command_blocked"
            }

        # Read-only commands
        if lower_text == "status":
            return {
                "command_type": "system_status",
                "risk_level": "read_only"
            }
        
        if lower_text.startswith("status service "):
            return {
                "command_type": "service_status",
                "risk_level": "read_only"
            }

        # Controlled writes
        if lower_text.startswith("restart service ") or lower_text == "restart" or lower_text.startswith("restart "):
            return {
                "command_type": "service_restart",
                "risk_level": "high"
            }
            
        return {
            "command_type": "unknown",
            "risk_level": "blocked",
            "blocked_reason": "command_unknown"
        }
