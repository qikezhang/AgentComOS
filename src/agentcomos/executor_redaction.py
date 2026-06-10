import re
from typing import Any, Dict, List, Optional

SECRET_PATTERNS = [
    re.compile(r'(?i)\b(DISCORD_BOT_TOKEN)=([^\s]+)'),
    re.compile(r'(?i)\b(DISCORD_TOKEN)=([^\s]+)'),
    re.compile(r'(?i)\b(BOT_TOKEN)=([^\s]+)'),
    re.compile(r'(?i)\b(token)=([^\s]+)'),
    re.compile(r'(?i)\b(secret)=([^\s]+)'),
    re.compile(r'(?i)\b(password)=([^\s]+)'),
    re.compile(r'(?i)\b(api_key)=([^\s]+)'),
    re.compile(r'(?i)\b(apikey)=([^\s]+)'),
    re.compile(r'(?i)\b(private_key)=([^\s]+)'),
    re.compile(r'BEGIN OPENSSH PRIVATE KEY(?:.|\n)*?END OPENSSH PRIVATE KEY', re.DOTALL),
    re.compile(r'BEGIN RSA PRIVATE KEY(?:.|\n)*?END RSA PRIVATE KEY', re.DOTALL),
    re.compile(r'BEGIN PRIVATE KEY(?:.|\n)*?END PRIVATE KEY', re.DOTALL),
]

SECRET_KEY_PATTERN = re.compile(r'(?i).*(token|secret|password|api_key|apikey|private_key).*')

def redact_executor_text(value: str) -> str:
    if not isinstance(value, str):
        return value
        
    redacted = value
    for pattern in SECRET_PATTERNS:
        if pattern.groups == 2:
            redacted = pattern.sub(lambda m: f"<redacted:{m.group(1).lower()}>", redacted)
        else:
            if "PRIVATE KEY" in pattern.pattern:
                redacted = pattern.sub("<redacted:private_key>", redacted)
            
    return redacted

def contains_secret_like_text(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return redact_executor_text(value) != value

def redact_executor_data(value: Any) -> Any:
    if isinstance(value, str):
        return redact_executor_text(value)
    elif isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if isinstance(k, str) and SECRET_KEY_PATTERN.match(k) and isinstance(v, str) and v != "":
                result[k] = f"<redacted:{k.lower()}>"
            else:
                result[k] = redact_executor_data(v)
        return result
    elif isinstance(value, list):
        return [redact_executor_data(v) for v in value]
    return value
