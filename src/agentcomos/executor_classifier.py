import re
from typing import Tuple, Optional

class ExecutorClassifier:
    """Classifies commands and assigns risk levels."""

    SECRET_PATTERNS = [
        re.compile(r"(?i)token=[^\s]+"),
        re.compile(r"(?i)password=[^\s]+"),
        re.compile(r"(?i)secret=[^\s]+"),
        re.compile(r"(?i)private\s*key"),
        re.compile(r"(?i)env"),
    ]

    DIRECT_SYSTEM_PATTERNS = [
        re.compile(r"^(bash|sh|zsh)(\s|$)"),
        re.compile(r"^ssh(\s|$)"),
        re.compile(r"^scp(\s|$)"),
        re.compile(r"^rsync(\s|$)"),
        re.compile(r"^sudo(\s|$)"),
        re.compile(r"^systemctl(\s|$)"),
        re.compile(r"^docker\s+(compose\s+)?(run|exec|build)(\s|$)"),
    ]

    DESTRUCTIVE_PATTERNS = [
        re.compile(r"rm\s+-rf"),
        re.compile(r"docker\s+system\s+prune"),
    ]

    @classmethod
    def classify_command(cls, command_text: str) -> Tuple[str, str, Optional[str]]:
        """
        Returns: (risk_level, status, reason)
        """
        cmd_lower = command_text.lower().strip()

        # Check for secrets
        for pattern in cls.SECRET_PATTERNS:
            if pattern.search(command_text):
                return "secret", "blocked", "secret_request_blocked"

        # Check for destructive
        for pattern in cls.DESTRUCTIVE_PATTERNS:
            if pattern.search(command_text):
                return "destructive", "blocked", "destructive_command_blocked"

        # Check for direct system commands
        for pattern in cls.DIRECT_SYSTEM_PATTERNS:
            if pattern.search(command_text):
                return "direct_system", "blocked", "direct_system_command_blocked"

        # Specific command types
        if cmd_lower.startswith("status") or cmd_lower.startswith("check"):
            return "read_only", "received", None
        elif cmd_lower.startswith("restart"):
            return "high", "requires_approval", "approval_required"
        elif cmd_lower.startswith("docker compose restart"):
            return "direct_system", "blocked", "direct_system_command_blocked"

        return "unknown", "blocked", "command_unknown"

    @classmethod
    def redact(cls, command_text: str) -> str:
        redacted = command_text
        for pattern in cls.SECRET_PATTERNS:
            if pattern.pattern == r"(?i)env" or pattern.pattern == r"(?i)private\s*key":
                continue # we just block these entirely, but if we redact:
            redacted = pattern.sub("REDACTED", redacted)
        return redacted
