from __future__ import annotations

import yaml
import agentcomos.controller.state as state
from agentcomos.frontier.builder import read_task_frontier

def generate_artifact_index(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    
    checks = [
        {"path": "run_status.yaml", "type": "run_status"},
        {"path": "events.jsonl", "type": "event_log"},
        {"path": "timeline.yaml", "type": "timeline"},
        {"path": "operating_program.yaml", "type": "operating_program"},
        {"path": "task_frontier.yaml", "type": "task_frontier"},
        {"path": "task_frontier_index.yaml", "type": "task_frontier_index"},
        {"path": "frontier_status.yaml", "type": "frontier_status"},
        {"path": "delivery_packet.yaml", "type": "delivery_packet"},
        {"path": "gm_report.md", "type": "gm_report"},
        {"path": "opencode_outputs/opencode_project_plan.yaml", "type": "opencode_output"},
        {"path": "worker_outputs/TF-001/result.yaml", "type": "worker_output"}
    ]
    
    # Scan decision directory
    decision_dir = run_dir / "decision"
    if decision_dir.exists() and decision_dir.is_dir():
        for task_dir in decision_dir.iterdir():
            if not task_dir.is_dir():
                continue
            task_id = task_dir.name
            if (task_dir / "decision_request.yaml").exists():
                checks.append({
                    "path": f"decision/{task_id}/decision_request.yaml",
                    "type": "decision_request",
                    "phase": "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION"
                })
                checks.append({
                    "path": f"decision/{task_id}/decision_result.yaml",
                    "type": "decision_result",
                    "phase": "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION"
                })
    
    # Scan feynman directory
    feynman_dir = run_dir / "feynman"
    if feynman_dir.exists() and feynman_dir.is_dir():
        for task_dir in feynman_dir.iterdir():
            if not task_dir.is_dir():
                continue
            task_id = task_dir.name
            if (task_dir / "feynman_check.yaml").exists():
                checks.append({
                    "path": f"feynman/{task_id}/feynman_check.yaml",
                    "type": "feynman_check",
                    "phase": "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION"
                })
                checks.append({
                    "path": f"feynman/{task_id}/feynman_result.yaml",
                    "type": "feynman_result",
                    "phase": "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION"
                })

    # Scan manual_os directory
    manual_os_dir = run_dir / "manual_os"
    if manual_os_dir.exists() and manual_os_dir.is_dir():
        for task_dir in manual_os_dir.iterdir():
            if not task_dir.is_dir():
                continue
            task_id = task_dir.name
            
            checks.append({
                "path": f"manual_os/{task_id}/manual_os_request.yaml",
                "type": "manual_os_request",
                "phase": "G10_MANUAL_OS_CONTROLLED_ADOPTION"
            })
            checks.append({
                "path": f"manual_os/{task_id}/manual_os_approval.yaml",
                "type": "manual_os_approval",
                "phase": "G10_MANUAL_OS_CONTROLLED_ADOPTION"
            })
            checks.append({
                "path": f"manual_os/{task_id}/manual_os_result.yaml",
                "type": "manual_os_result",
                "phase": "G10_MANUAL_OS_CONTROLLED_ADOPTION"
            })
            checks.append({
                "path": f"manual_os/{task_id}/manual_os_audit.md",
                "type": "manual_os_audit",
                "phase": "G10_MANUAL_OS_CONTROLLED_ADOPTION"
            })

    if (run_dir / "loop_plan.yaml").exists() or (run_dir / "loop_status.yaml").exists():
        checks.extend([
            {
                "path": "loop_plan.yaml",
                "type": "loop_plan",
                "phase": "G9_LOOP_EXECUTION"
            },
            {
                "path": "loop_status.yaml",
                "type": "loop_status",
                "phase": "G9_LOOP_EXECUTION"
            },
            {
                "path": "loop_trace.yaml",
                "type": "loop_trace",
                "phase": "G9_LOOP_EXECUTION"
            },
            {
                "path": "loop_summary.md",
                "type": "loop_summary",
                "phase": "G9_LOOP_EXECUTION"
            }
        ])



    checks.sort(key=lambda x: x["path"])

    artifacts = []
    for check in checks:
        exists = (run_dir / check["path"]).exists()
        entry = {
            "path": check["path"],
            "type": check["type"],
            "exists": exists
        }
        if "phase" in check:
            entry["phase"] = check["phase"]
        artifacts.append(entry)
        
    index = {
        "run_id": run_id,
        "artifacts": artifacts
    }
    
    path = run_dir / "evidence_packet" / "artifact_index.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(index, sort_keys=False), encoding="utf-8")
