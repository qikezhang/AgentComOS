import yaml
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import read_events

def build_timeline(run_id: str, current_state: str) -> None:
    events = read_events(run_id)
    timeline_events = []
    for e in events:
        t = {"type": e["type"], "timestamp": e["timestamp"]}
        if "from_state" in e.get("payload", {}):
            t["from_state"] = e["payload"]["from_state"]
        if "to_state" in e.get("payload", {}):
            t["to_state"] = e["payload"]["to_state"]
        timeline_events.append(t)
    
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
        "produced_by": "controller",
        "status": "completed",
        "summary": "G1 fake controller run completed.",
        "artifacts": [
            "run_status.yaml",
            "events.jsonl",
            "timeline.yaml"
        ],
        "risks": [],
        "next_actions": [
            "Ready for Codex G1 review."
        ]
    }
    path.write_text(yaml.dump(packet, sort_keys=False), encoding="utf-8")
