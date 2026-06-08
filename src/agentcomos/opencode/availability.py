import shutil
from datetime import datetime, timezone

def is_opencode_available() -> bool:
    """Check if the opencode binary is available in PATH."""
    return shutil.which("opencode") is not None

def check_opencode_availability() -> dict:
    """Check opencode availability and return a status dict."""
    available = is_opencode_available()
    return {
        "available": available,
        "reason": "" if available else "opencode not found",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "version": "unknown",
        "runtime": "real_opencode",
        "mode": "real",
        "hostname": "127.0.0.1",
        "port": 4096
    }
