from enum import Enum
from pathlib import Path
from typing import Any
import yaml

class RunState(str, Enum):
    created = "created"
    accepted = "accepted"
    context_ready = "context_ready"
    planning = "planning"
    executing = "executing"
    evidence_verifying = "evidence_verifying"
    delivery_ready = "delivery_ready"
    reported = "reported"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"
    paused = "paused"

def get_run_dir(run_id: str) -> Path:
    return Path(".agentcomos") / "runs" / run_id

def read_run_status(run_id: str) -> dict[str, Any] | None:
    path = get_run_dir(run_id) / "run_status.yaml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def write_run_status(run_id: str, status: dict[str, Any]) -> None:
    path = get_run_dir(run_id) / "run_status.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(status, sort_keys=False), encoding="utf-8")

def get_next_fake_state(current: RunState) -> RunState:
    transitions = {
        RunState.created: RunState.accepted,
        RunState.accepted: RunState.context_ready,
        RunState.context_ready: RunState.planning,
        RunState.planning: RunState.executing,
        RunState.executing: RunState.evidence_verifying,
        RunState.evidence_verifying: RunState.delivery_ready,
        RunState.delivery_ready: RunState.completed,
        RunState.completed: RunState.completed,
    }
    return transitions.get(current, current)
