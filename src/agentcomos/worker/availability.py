import shutil
import yaml
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def check_hermes_availability() -> dict:
    """Check if the Hermes CLI is available and write status artifact."""
    path = shutil.which("hermes")
    available = bool(path)
    version = "unknown"
    if available:
        try:
            result = subprocess.run(["hermes", "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                version = result.stdout.strip()
        except Exception:
            pass

    status = {
        "available": available,
        "reason": "" if available else "hermes not found",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "version": version,
        "runtime": "real_hermes"
    }

    # Write status artifact
    status_dir = Path(".agentcomos/worker-runtime")
    status_dir.mkdir(parents=True, exist_ok=True)
    status_file = status_dir / "hermes_runtime_status.yaml"
    with open(status_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(status, f, sort_keys=False)

    return status
