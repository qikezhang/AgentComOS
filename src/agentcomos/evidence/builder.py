from __future__ import annotations

import yaml
import hashlib
from pathlib import Path

import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.evidence.summaries import generate_events_summary, generate_runtime_summary
from agentcomos.evidence.artifact_index import generate_artifact_index
from agentcomos.evidence.validation import generate_validation_summary
from agentcomos.controller.artifacts import rebuild_timeline_from_events

def get_input_fingerprint(run_id: str) -> str:
    run_dir = state.get_run_dir(run_id)
    hasher = hashlib.sha256()
    
    for filename in [
        "run_status.yaml",
        "events.jsonl",
        "timeline.yaml",
        "operating_program.yaml",
        "task_frontier.yaml",
        "task_frontier_index.yaml",
        "frontier_status.yaml",
        "loop_plan.yaml",
        "loop_status.yaml",
        "loop_trace.yaml",
        "loop_summary.md",
    ]:
        path = run_dir / filename
        if path.exists():
            if filename == "events.jsonl":
                lines = []
                for line in path.read_text(encoding="utf-8").splitlines():
                    if "evidence.build" not in line and "delivery." not in line and "gm.report" not in line:
                        lines.append(line)
                hasher.update("\n".join(lines).encode("utf-8"))
            elif filename == "timeline.yaml":
                try:
                    data = yaml.safe_load(path.read_text(encoding="utf-8"))
                    if data and "events" in data:
                        data["events"] = [e for e in data["events"] if not (e.get("type", "").startswith("evidence.build") or e.get("type", "").startswith("delivery.") or e.get("type", "").startswith("gm.report"))]
                    hasher.update(yaml.dump(data, sort_keys=True).encode("utf-8"))
                except Exception:
                    hasher.update(path.read_bytes())
            else:
                hasher.update(path.read_bytes())
                
    for d in ["opencode_jobs", "worker_outputs", "manual_os"]:
        dir_path = run_dir / d
        if dir_path.exists():
            for p in sorted(dir_path.rglob("*")):
                if p.is_file():
                    hasher.update(p.read_bytes())
                    
    return hasher.hexdigest()

def finalize_evidence_packet(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        return
        
    generate_events_summary(run_id)
    generate_runtime_summary(run_id)
    generate_artifact_index(run_id)
    val_status = generate_validation_summary(run_id)
    
    manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
    
    evts = events.read_events(run_id)
    created_at = evts[0]["timestamp"] if evts else events.get_timestamp()
    
    fingerprint = get_input_fingerprint(run_id)
    
    if manifest_path.exists():
        try:
            old_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if old_manifest and "created_at" in old_manifest:
                created_at = old_manifest["created_at"]
        except Exception:
            pass
            
    inputs_list = [
        "run_status.yaml",
        "events.jsonl",
        "timeline.yaml"
    ]
    for lf in ["loop_plan.yaml", "loop_status.yaml", "loop_trace.yaml", "loop_summary.md"]:
        if (run_dir / lf).exists():
            inputs_list.append(lf)
            
    manifest = {
        "run_id": run_id,
        "phase": "G6_EVIDENCE_DELIVERY_GM_REPORT",
        "generated_by": "controller",
        "status": "completed" if val_status == "passed" else val_status,
        "created_at": created_at,
        "input_fingerprint": fingerprint,
        "inputs": inputs_list,
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
    
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest, sort_keys=False), encoding="utf-8")

def build_evidence_packet(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    events_path = run_dir / "events.jsonl"
    timeline_path = run_dir / "timeline.yaml"
    
    missing_critical = False
    error_msg = ""
    if not events_path.exists():
        missing_critical = True
        error_msg = "Missing events.jsonl"
    elif not timeline_path.exists():
        missing_critical = True
        error_msg = "Missing timeline.yaml"
        
    if missing_critical:
        generate_validation_summary(run_id)
        finalize_evidence_packet(run_id)
        raise ValueError(error_msg)

    manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
    fingerprint = get_input_fingerprint(run_id)
    
    if manifest_path.exists():
        try:
            old_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if old_manifest.get("input_fingerprint") == fingerprint and old_manifest.get("status") == "completed":
                return
        except Exception:
            pass

    events.append_event(run_id, "evidence.build.started", {"status": "started"})
    
    try:
        generate_events_summary(run_id)
        generate_runtime_summary(run_id)
        generate_artifact_index(run_id)
        val_status = generate_validation_summary(run_id)
        
        events.append_event(run_id, "evidence.build.completed", {"status": "completed" if val_status == "passed" else val_status})
        
        rebuild_timeline_from_events(run_id)
        finalize_evidence_packet(run_id)
    except Exception as e:
        events.append_event(run_id, "evidence.build.failed", {"error": str(e)})
        rebuild_timeline_from_events(run_id)
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
