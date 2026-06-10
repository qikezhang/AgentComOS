import re
from typing import Any, Dict, List, Union

def redact_string(value: str) -> str:
    """Redact tokens, secrets and keys from a string."""
    if not isinstance(value, str):
        return value
        
    redacted = value
    
    # Redact obvious token patterns
    redacted = re.sub(r"(DISCORD_BOT_TOKEN)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(DISCORD_TOKEN)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(BOT_TOKEN)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(token)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(secret)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(password)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(api_key)=([^\s]+)", r"\1=***REDACTED***", redacted, flags=re.IGNORECASE)
    
    # Redact similar patterns with colons (YAML/JSON style)
    redacted = re.sub(r"(token):\s*([^\s,]+)", r"\1: ***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(secret):\s*([^\s,]+)", r"\1: ***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(password):\s*([^\s,]+)", r"\1: ***REDACTED***", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(api_key):\s*([^\s,]+)", r"\1: ***REDACTED***", redacted, flags=re.IGNORECASE)

    # Redact Private Keys
    redacted = re.sub(r"-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----", "***REDACTED PRIVATE KEY***", redacted, flags=re.DOTALL)
    redacted = re.sub(r"-----BEGIN OPENSSH PRIVATE KEY-----.*?-----END OPENSSH PRIVATE KEY-----", "***REDACTED PRIVATE KEY***", redacted, flags=re.DOTALL)
    redacted = re.sub(r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----", "***REDACTED PRIVATE KEY***", redacted, flags=re.DOTALL)

    return redacted

def redact_data(data: Union[Dict, List, str, Any]) -> Union[Dict, List, str, Any]:
    """Recursively redact a data structure."""
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: redact_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_data(v) for v in data]
    return data
