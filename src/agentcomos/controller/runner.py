from pathlib import Path
import shutil
import yaml
from agentcomos.controller.state import RunState, get_run_dir, read_run_status, write_run_status, get_next_fake_state
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
    run_dir = get_run_dir(run_id)
    shutil.copyfile(intent_path, run_dir / "operating_intent.yaml")
    append_event(run_id, "run.created", {"intent_file": str(intent_path)})
    build_timeline(run_id, RunState.created.value)
    print(f"Run {run_id} created.")

def handle_run_status(run_id: str) -> None:
    status = read_run_status(run_id)
    if not status:
        raise ValueError(f"Run {run_id} not found.")
    print(yaml.dump(status, sort_keys=False))

def handle_controller_tick(run_id: str, fake: bool) -> dict | None:
    status = read_run_status(run_id)
    if not status:
        raise ValueError(f"Run {run_id} not found.")
    
    try:
        current_state = RunState(status["state"])
    except ValueError:
        raise ValueError(f"Invalid state: {status['state']}")
        
    append_event(run_id, "controller.tick.started", {"fake": fake})
    
    g7_result = None
    if fake:
        next_state = get_next_fake_state(current_state)
        if next_state != current_state:
            status["state"] = next_state.value
            
            if next_state == RunState.planning:
                from agentcomos.opencode.fake_runtime import submit_fake_job
                job_id = submit_fake_job(run_id)
                status["last_job_id"] = job_id
                status["phase"] = "G2_FAKE_OPENCODE_RUNTIME"
                
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

        g7_result = _handle_g7_fake_tick(run_id)
    
    current_state_str = status["state"]
    build_timeline(run_id, current_state_str)
    append_event(run_id, "controller.tick.completed", {"state": current_state_str})
    if g7_result:
        print(f"Tick completed. Current state: {current_state_str}. Frontier: {g7_result}")
    else:
        print(f"Tick completed. Current state: {current_state_str}")
    return g7_result


def _handle_g7_fake_tick(run_id: str) -> dict | None:
    run_dir = get_run_dir(run_id)
    intent_path = run_dir / "operating_intent.yaml"
    if not intent_path.exists():
        return None
    try:
        intent = yaml.safe_load(intent_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    if not (intent.get("goal") or intent.get("objective")):
        return None

    from agentcomos.frontier.builder import build_task_frontier, read_task_frontier
    from agentcomos.frontier.executor import advance_one_frontier_task
    from agentcomos.frontier.status import generate_frontier_status
    from agentcomos.program.builder import build_operating_program

    build_operating_program(run_id)
    if not read_task_frontier(run_id):
        build_task_frontier(run_id)
    result = advance_one_frontier_task(run_id)
    generate_frontier_status(run_id)
    return result

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
