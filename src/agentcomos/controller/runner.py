from pathlib import Path
import yaml
from agentcomos.controller.state import RunState, read_run_status, write_run_status, get_next_fake_state
from agentcomos.controller.events import append_event, read_events
from agentcomos.controller.artifacts import build_timeline, build_evidence_packet, build_delivery_packet

def handle_run_create(intent_path: Path) -> None:
    if not intent_path.exists():
        raise ValueError(f"Intent file not found: {intent_path}")
    intent = yaml.safe_load(intent_path.read_text(encoding="utf-8"))
    run_id = intent.get("intent_id") or intent.get("run_id")
    if not run_id:
        raise ValueError("Intent file missing intent_id/run_id")
    
    status = read_run_status(run_id)
    if status is not None:
        print(f"Run {run_id} already exists.")
        return
    
    status = {
        "run_id": run_id,
        "state": RunState.created.value,
    }
    write_run_status(run_id, status)
    append_event(run_id, "run.created", {"intent_file": str(intent_path)})
    build_timeline(run_id, RunState.created.value)
    print(f"Run {run_id} created.")

def handle_run_status(run_id: str) -> None:
    status = read_run_status(run_id)
    if not status:
        raise ValueError(f"Run {run_id} not found.")
    print(yaml.dump(status, sort_keys=False))

def handle_controller_tick(run_id: str, fake: bool) -> None:
    status = read_run_status(run_id)
    if not status:
        raise ValueError(f"Run {run_id} not found.")
    
    try:
        current_state = RunState(status["state"])
    except ValueError:
        raise ValueError(f"Invalid state: {status['state']}")
        
    append_event(run_id, "controller.tick.started", {"fake": fake})
    
    if fake:
        next_state = get_next_fake_state(current_state)
        if next_state != current_state:
            status["state"] = next_state.value
            write_run_status(run_id, status)
            append_event(run_id, "run.state_changed", {
                "from_state": current_state.value,
                "to_state": next_state.value
            })
            
            if next_state in (RunState.evidence_verifying, RunState.delivery_ready, RunState.reported, RunState.completed):
                build_evidence_packet(run_id)
                append_event(run_id, "evidence.built", {})
                
            if next_state in (RunState.delivery_ready, RunState.reported, RunState.completed):
                build_delivery_packet(run_id)
                append_event(run_id, "delivery.built", {})
    
    current_state_str = status["state"]
    build_timeline(run_id, current_state_str)
    append_event(run_id, "controller.tick.completed", {"state": current_state_str})
    print(f"Tick completed. Current state: {current_state_str}")

def handle_controller_recover(run_id: str) -> None:
    events = read_events(run_id)
    if not events:
        raise ValueError(f"No events found for run {run_id}. Cannot recover.")
    
    current_state = RunState.created.value
    for e in events:
        if e["type"] == "run.created":
            current_state = RunState.created.value
        elif e["type"] == "run.state_changed":
            current_state = e["payload"].get("to_state", current_state)
    
    status = read_run_status(run_id)
    if not status:
        status = {"run_id": run_id, "state": current_state}
    else:
        status["state"] = current_state
    
    write_run_status(run_id, status)
    append_event(run_id, "controller.recovered", {"recovered_state": current_state})
    build_timeline(run_id, current_state)
    print(f"Run {run_id} recovered to state {current_state}.")
