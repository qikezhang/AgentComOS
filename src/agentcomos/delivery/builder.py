from __future__ import annotations

import yaml
import agentcomos.controller.events as events
import agentcomos.controller.state as state

def build_delivery_packet(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    events.append_event(run_id, "delivery.build.started", {"status": "started"})
    
    try:
        manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
        events_path = run_dir / "events.jsonl"
        timeline_path = run_dir / "timeline.yaml"
        
        has_critical = manifest_path.exists() and events_path.exists() and timeline_path.exists()
        evidence_status = "failed"
        if manifest_path.exists():
            ev = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            evidence_status = ev.get("status", "failed")
            
        status = "completed"
        if not has_critical or evidence_status == "failed":
            status = "failed"
        elif evidence_status == "partial":
            status = "partial"
            
        packet = {
            "packet_id": f"DP-{run_id}",
            "run_id": run_id,
            "produced_by": ["controller", "evidence_builder"],
            "status": status,
            "summary": "Delivery packet generated from evidence.",
            "artifacts": [
                "run_status.yaml",
                "events.jsonl",
                "timeline.yaml",
                "evidence_packet/manifest.yaml",
                "evidence_packet/events_summary.yaml",
                "evidence_packet/runtime_summary.yaml",
                "evidence_packet/artifact_index.yaml",
                "evidence_packet/validation_summary.yaml",
                "gm_report.md"
            ],
            "risks": [],
            "next_actions": ["Ready for Codex G6 review."]
        }
        
        path = run_dir / "delivery_packet.yaml"
        path.write_text(yaml.dump(packet, sort_keys=False), encoding="utf-8")
        
        events.append_event(run_id, "delivery.updated", {"packet_id": packet["packet_id"]})
        events.append_event(run_id, "delivery.build.completed", {"status": status})
    except Exception as e:
        events.append_event(run_id, "delivery.build.failed", {"error": str(e)})
        raise

def get_delivery_status(run_id: str) -> str:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        return "missing_run"
    path = run_dir / "delivery_packet.yaml"
    if not path.exists():
        return "missing_packet"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("status", "unknown")
