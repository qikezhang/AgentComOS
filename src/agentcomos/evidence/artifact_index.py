from __future__ import annotations

import yaml
import agentcomos.controller.state as state

def generate_artifact_index(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    
    checks = [
        {"path": "run_status.yaml", "type": "run_status"},
        {"path": "events.jsonl", "type": "event_log"},
        {"path": "timeline.yaml", "type": "timeline"},
        {"path": "delivery_packet.yaml", "type": "delivery_packet"},
        {"path": "gm_report.md", "type": "gm_report"},
        {"path": "opencode_outputs/opencode_project_plan.yaml", "type": "opencode_output"},
        {"path": "worker_outputs/TF-001/result.yaml", "type": "worker_output"}
    ]
    
    artifacts = []
    for check in checks:
        exists = (run_dir / check["path"]).exists()
        artifacts.append({
            "path": check["path"],
            "type": check["type"],
            "exists": exists
        })
        
    index = {
        "run_id": run_id,
        "artifacts": artifacts
    }
    
    path = run_dir / "evidence_packet" / "artifact_index.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(index, sort_keys=False), encoding="utf-8")
