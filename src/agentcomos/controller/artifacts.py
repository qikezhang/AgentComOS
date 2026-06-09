import yaml
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import read_events

def build_timeline(run_id: str, current_state: str) -> None:
    events = read_events(run_id)
    timeline_events = []
    for e in events:
        t = {
            "event_id": e.get("event_id"),
            "type": e["type"],
            "timestamp": e["timestamp"],
            "actor": e.get("actor", "controller"),
        }
        if "from_state" in e.get("payload", {}):
            t["from_state"] = e["payload"]["from_state"]
        if "to_state" in e.get("payload", {}):
            t["to_state"] = e["payload"]["to_state"]
        if "task_id" in e.get("payload", {}):
            t["task_id"] = e["payload"]["task_id"]
        for k in ["stop_reason", "tick_number", "tick_result", "advanced_task_id", "max_ticks"]:
            if k in e.get("payload", {}):
                t[k] = e["payload"][k]
        timeline_events.append(t)
    
    timeline = {
        "run_id": run_id,
        "current_state": current_state,
        "events": timeline_events,
    }
    path = get_run_dir(run_id) / "timeline.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(timeline, sort_keys=False), encoding="utf-8")

def rebuild_timeline_from_events(run_id: str) -> None:
    events = read_events(run_id)
    seen_ids = set()
    timeline_events = []
    for e in events:
        eid = e.get("event_id")
        if eid and eid in seen_ids:
            continue
        if eid:
            seen_ids.add(eid)
        
        t = {"event_id": eid, "type": e["type"], "timestamp": e["timestamp"], "actor": e.get("actor", "controller")}
        if "from_state" in e.get("payload", {}):
            t["from_state"] = e["payload"]["from_state"]
        if "to_state" in e.get("payload", {}):
            t["to_state"] = e["payload"]["to_state"]
        if "task_id" in e.get("payload", {}):
            t["task_id"] = e["payload"]["task_id"]
        for k in ["stop_reason", "tick_number", "tick_result", "advanced_task_id", "max_ticks"]:
            if k in e.get("payload", {}):
                t[k] = e["payload"][k]
        timeline_events.append(t)
    
    current_state = "unknown"
    status_path = get_run_dir(run_id) / "run_status.yaml"
    if status_path.exists():
        try:
            status_data = yaml.safe_load(status_path.read_text(encoding="utf-8"))
            current_state = status_data.get("current_state") or status_data.get("state", "unknown")
        except Exception:
            pass
            
    timeline = {
        "run_id": run_id,
        "current_state": current_state,
        "events": timeline_events,
    }
    path = get_run_dir(run_id) / "timeline.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(timeline, sort_keys=False), encoding="utf-8")

def build_evidence_packet(run_id: str) -> None:
    path = get_run_dir(run_id) / "evidence_packet" / "manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "phase": "G1_CONTROLLER_MINIMUM_STATE_MACHINE",
        "artifacts": [
            "../run_status.yaml",
            "../events.jsonl",
            "../timeline.yaml",
            "../delivery_packet.yaml"
        ],
        "validation": {
            "fake_runtime": True,
            "real_opencode_used": False,
            "real_hermes_used": False
        }
    }
    path.write_text(yaml.dump(manifest, sort_keys=False), encoding="utf-8")

def build_delivery_packet(run_id: str) -> None:
    path = get_run_dir(run_id) / "delivery_packet.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    packet = {
        "packet_id": f"DP-{run_id}",
        "run_id": run_id,
        "produced_by": [
            "controller",
            "fake_opencode"
        ],
        "status": "completed",
        "summary": "G2 fake OpenCode runtime completed.",
        "artifacts": [
            "run_status.yaml",
            "events.jsonl",
            "timeline.yaml"
        ],
        "risks": [],
        "next_actions": [
            "Ready for Codex G2 review."
        ]
    }
    
    # Conditionally add opencode outputs
    job_id = f"OCJ-{run_id}-001"
    job_path = get_run_dir(run_id) / "opencode_jobs" / f"{job_id}.yaml"
    plan_path = get_run_dir(run_id) / "opencode_outputs" / "opencode_project_plan.yaml"
    
    if job_path.exists():
        packet["artifacts"].append(f"opencode_jobs/{job_id}.yaml")
    if plan_path.exists():
        packet["artifacts"].append("opencode_outputs/opencode_project_plan.yaml")
        
    path.write_text(yaml.dump(packet, sort_keys=False), encoding="utf-8")
    
    # Ensure delivery.updated event is appended as required by G2
    from agentcomos.controller.events import append_event
    append_event(run_id, "delivery.updated", {"packet_id": packet["packet_id"]})
