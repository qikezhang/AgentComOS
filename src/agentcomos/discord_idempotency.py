from pathlib import Path
from typing import Optional, Dict
import yaml

def check_duplicate(runtime_dir: Path, message_id: str) -> Optional[Dict]:
    """Check if the message_id has already been processed."""
    idempotency_file = runtime_dir / "idempotency" / f"{message_id}.yaml"
    if idempotency_file.exists():
        return yaml.safe_load(idempotency_file.read_text(encoding="utf-8"))
    return None

def record_message(runtime_dir: Path, message_id: str, gm_command_id: Optional[str] = None, status: str = "processed"):
    """Record a message as processed."""
    idempotency_dir = runtime_dir / "idempotency"
    idempotency_dir.mkdir(parents=True, exist_ok=True)
    
    idempotency_file = idempotency_dir / f"{message_id}.yaml"
    data = {
        "message_id": message_id,
        "gm_command_id": gm_command_id,
        "status": status
    }
    idempotency_file.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
