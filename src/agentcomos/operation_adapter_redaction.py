import re
from typing import Dict, Any, Union

def redact_adapter_text(text: str) -> str:
    if not text:
        return text
    
    redacted = text
    patterns = [
        (r"(?i)token=[^\s&]+", "token=[REDACTED]"),
        (r"(?i)password=[^\s&]+", "password=[REDACTED]"),
        (r"(?i)secret=[^\s&]+", "secret=[REDACTED]"),
        (r"(?i)api_key=[^\s&]+", "api_key=[REDACTED]"),
        (r"DISCORD_BOT_TOKEN=[^\s]+", "DISCORD_BOT_TOKEN=[REDACTED]"),
        (r"DISCORD_TOKEN=[^\s]+", "DISCORD_TOKEN=[REDACTED]"),
        (r"BOT_TOKEN=[^\s]+", "BOT_TOKEN=[REDACTED]"),
        (r"BEGIN OPENSSH PRIVATE KEY[\s\S]+?END OPENSSH PRIVATE KEY", "[REDACTED PRIVATE KEY]"),
        (r"BEGIN RSA PRIVATE KEY[\s\S]+?END RSA PRIVATE KEY", "[REDACTED PRIVATE KEY]"),
        (r"PRIVATE KEY[\s\S]+?PRIVATE KEY", "[REDACTED PRIVATE KEY]")
    ]
    
    for pattern, replacement in patterns:
        redacted = re.sub(pattern, replacement, redacted)
        
    return redacted

def redact_adapter_data(data: Union[Dict[str, Any], list, str]) -> Union[Dict[str, Any], list, str]:
    if isinstance(data, str):
        return redact_adapter_text(data)
    elif isinstance(data, list):
        return [redact_adapter_data(item) for item in data]
    elif isinstance(data, dict):
        result = {}
        for k, v in data.items():
            result[k] = redact_adapter_data(v)
        return result
    return data
