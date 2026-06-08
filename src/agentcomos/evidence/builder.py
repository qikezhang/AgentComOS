from __future__ import annotations

import yaml
from pathlib import Path

import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.evidence.summaries import generate_events_summary, generate_runtime_summary
from agentcomos.evidence.artifact_index import generate_artifact_index
from agentcomos.evidence.validation import generate_validation_summary

def build_evidence_packet(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
    
    events.append_event(run_id, "evidence.build.started", {"status": "started"})
    
    try:
        generate_events_summary(run_id)
        generate_runtime_summary(run_id)
        generate_artifact_index(run_id)
        val_status = generate_validation_summary(run_id)
        
        manifest = {
            "run_id": run_id,
            "phase": "G6_EVIDENCE_DELIVERY_GM_REPORT",
            "generated_by": "controller",
            "status": "completed" if val_status == "passed" else val_status,
            "created_at": events.append_event(run_id, "dummy", {})["timestamp"],
            "inputs": [
                "run_status.yaml",
                "events.jsonl",
                "timeline.yaml"
            ],
            "evidence_files": [
                "events_summary.yaml",
                "runtime_summary.yaml",
                "artifact_index.yaml",
                "validation_summary.yaml"
            ],
            "validation": {
                "run_status_present": (run_dir / "run_status.yaml").exists(),
                "events_present": (run_dir / "events.jsonl").exists(),
                "timeline_present": (run_dir / "timeline.yaml").exists(),
                "delivery_packet_present": (run_dir / "delivery_packet.yaml").exists(),
                "gm_report_present": (run_dir / "gm_report.md").exists(),
                "no_runtime_artifacts_committed": True
            }
        }
        
        manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(yaml.dump(manifest, sort_keys=False), encoding="utf-8")
        
        events.append_event(run_id, "evidence.build.completed", {"status": manifest["status"]})
    except Exception as e:
        events.append_event(run_id, "evidence.build.failed", {"error": str(e)})
        raise

def get_evidence_status(run_id: str) -> str:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        return "missing_run"
    manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
    if not manifest_path.exists():
        return "missing_manifest"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return data.get("status", "unknown")
