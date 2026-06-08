import json
import uuid
from datetime import datetime, timezone
from typing import Any
from agentcomos.controller.state import get_run_dir

def generate_event_id() -> str:
    return f"EVT-{uuid.uuid4().hex[:8].upper()}"

def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def append_event(run_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_id": generate_event_id(),
        "run_id": run_id,
        "type": event_type,
        "timestamp": get_timestamp(),
        "actor": "controller",
        "payload": payload,
    }
    path = get_run_dir(run_id) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return event

def read_events(run_id: str) -> list[dict[str, Any]]:
    path = get_run_dir(run_id) / "events.jsonl"
    if not path.exists():
        return []
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events
