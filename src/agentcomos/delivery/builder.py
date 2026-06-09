from __future__ import annotations

import yaml
import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.evidence.builder import finalize_evidence_packet, get_input_fingerprint, get_evidence_status
from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.frontier.builder import read_task_frontier

def build_delivery_packet(run_id: str) -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    path = run_dir / "delivery_packet.yaml"
    fingerprint = get_input_fingerprint(run_id)
    if path.exists():
        try:
            old_packet = yaml.safe_load(path.read_text(encoding="utf-8"))
            if old_packet.get("input_fingerprint") == fingerprint and old_packet.get("status") == "completed":
                return
        except Exception:
            pass

    evidence_status = get_evidence_status(run_id)
        
    events.append_event(run_id, "delivery.build.started", {"status": "started"})
    
    try:
        manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
        events_path = run_dir / "events.jsonl"
        timeline_path = run_dir / "timeline.yaml"
        
        has_critical = manifest_path.exists() and events_path.exists() and timeline_path.exists()
        
        frontier_status_path = run_dir / "frontier_status.yaml"
        frontier_status = {}
        if frontier_status_path.exists():
            frontier_status = yaml.safe_load(frontier_status_path.read_text(encoding="utf-8")) or {}
        failed_tasks_count = len(frontier_status.get("failed_tasks", []))
        
        frontier = read_task_frontier(run_id) or {}
        g8_controls = {"decision": [], "feynman": []}
        
        awaiting_d = len(frontier_status.get("awaiting_decision_tasks", [])) > 0
        awaiting_f = len(frontier_status.get("awaiting_feynman_tasks", [])) > 0
        awaiting_m = len(frontier_status.get("awaiting_manual_os_tasks", [])) > 0
        missing_required = False
        
        for task in frontier.get("tasks", []):
            task_id = task.get("task_id")
            if task.get("decision_required") or (run_dir / "decision" / task_id / "decision_request.yaml").exists():
                result_path = run_dir / "decision" / task_id / "decision_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_decision" if task_id in frontier_status.get("awaiting_decision_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                g8_controls["decision"].append({
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"decision/{task_id}/decision_result.yaml"
                })
            if task.get("feynman_required") or (run_dir / "feynman" / task_id / "feynman_check.yaml").exists():
                result_path = run_dir / "feynman" / task_id / "feynman_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_feynman" if task_id in frontier_status.get("awaiting_feynman_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                g8_controls["feynman"].append({
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"feynman/{task_id}/feynman_result.yaml"
                })
            if task.get("manual_os_required") or (run_dir / "manual_os" / task_id / "manual_os_request.yaml").exists():
                result_path = run_dir / "manual_os" / task_id / "manual_os_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_manual_os" if task_id in frontier_status.get("awaiting_manual_os_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                g8_controls.setdefault("manual_os", []).append({
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"manual_os/{task_id}/manual_os_result.yaml"
                })

        status = "completed"
        if not has_critical or evidence_status == "failed" or failed_tasks_count > 0:
            status = "failed"
        elif evidence_status == "partial" or awaiting_d or awaiting_f or awaiting_m or missing_required:
            status = "partial"
            
        artifacts_list = [
            "run_status.yaml",
            "events.jsonl",
            "timeline.yaml",
            "operating_program.yaml",
            "task_frontier.yaml",
            "task_frontier_index.yaml",
            "frontier_status.yaml"
        ]
        
        for lf in ["loop_plan.yaml", "loop_status.yaml", "loop_trace.yaml", "loop_summary.md"]:
            if (run_dir / lf).exists():
                artifacts_list.append(lf)
                
        artifacts_list.extend([
            "evidence_packet/manifest.yaml",
            "evidence_packet/events_summary.yaml",
            "evidence_packet/runtime_summary.yaml",
            "evidence_packet/artifact_index.yaml",
            "evidence_packet/validation_summary.yaml",
        ])
        
        g8_artifacts = []
        if (run_dir / "decision").exists():
            for p in (run_dir / "decision").glob("*/*.yaml"):
                g8_artifacts.append(str(p.relative_to(run_dir)))
        if (run_dir / "feynman").exists():
            for p in (run_dir / "feynman").glob("*/*.yaml"):
                g8_artifacts.append(str(p.relative_to(run_dir)))
        if (run_dir / "manual_os").exists():
            for p in (run_dir / "manual_os").glob("*/*.yaml"):
                g8_artifacts.append(str(p.relative_to(run_dir)))
            for p in (run_dir / "manual_os").glob("*/*.md"):
                g8_artifacts.append(str(p.relative_to(run_dir)))
        g8_artifacts.sort()
        artifacts_list.extend(g8_artifacts)
        artifacts_list.append("gm_report.md")

        risks = []
        next_actions = ["Review current delivery packet and proceed to the next approved phase after Codex acceptance."]
        if awaiting_d:
            risks.append("Task frontier has tasks awaiting_decision")
        if awaiting_f:
            risks.append("Task frontier has tasks awaiting_feynman")
        if awaiting_m:
            blocking_task_ids = frontier_status.get("awaiting_manual_os_tasks", [])
            risks.append(f"Task frontier has tasks awaiting_manual_os: {blocking_task_ids}")
            next_actions = [f"human approval/result required for manual OS tasks: {blocking_task_ids}"]
        g11_artifacts = []
        g11_controls = {"commands": []}
        gmd_dir = run_dir / "gm_\x64iscord"
        if gmd_dir.exists():
            for p in gmd_dir.rglob("*.*"):
                if p.is_file():
                    g11_artifacts.append(str(p.relative_to(run_dir)))
            if (gmd_dir / "commands").exists():
                for cmd_file in (gmd_dir / "commands").glob("*.yaml"):
                    cmd = yaml.safe_load(cmd_file.read_text(encoding="utf-8"))
                    cmd_id = cmd.get("command_id")
                    
                    res_status = "missing"
                    reason = cmd.get("reason", "unknown")
                    res_path = gmd_dir / "results" / f"{cmd_id}.yaml"
                    if res_path.exists():
                        res = yaml.safe_load(res_path.read_text(encoding="utf-8"))
                        res_status = res.get("status", "unknown")
                        reason = res.get("summary", reason)
                    else:
                        if cmd.get("status") == "blocked":
                            res_status = "blocked"
                        elif cmd.get("requires_confirmation"):
                            res_status = "requires_confirmation"
                        elif cmd.get("status") == "failed_parse":
                            res_status = "failed_parse"
                    
                    if res_status in ["blocked", "requires_confirmation", "failed_parse"] or reason in ["max_ticks_exceeds_g11_limit", "prohibited_shell_command", "fake_required", "real_runtime_loop_forbidden"]:
                        risks.append(f"GM \x44iscord command {cmd_id} is {res_status} with reason {reason}")
                        next_actions = [f"human action required to fix or confirm GM \x44iscord command {cmd_id}"]
                        if status == "completed":
                            status = "partial"
                            
                    g11_controls["commands"].append({
                        "command_id": cmd_id,
                        "status": res_status,
                        "reason": reason,
                        "artifact": f"gm_\x64iscord/commands/{cmd_id}.yaml"
                    })
        g11_artifacts.sort()
        artifacts_list.extend(g11_artifacts)

        if missing_required:
            risks.append("Missing required decision, feynman, or manual_os results")

        packet = {
            "packet_id": f"DP-{run_id}",
            "run_id": run_id,
            "produced_by": ["controller", "evidence_builder"],
            "status": status,
            "input_fingerprint": fingerprint,
            "summary": "Delivery packet generated from evidence.",
            "g8_controls": g8_controls,
            "g11_controls": g11_controls,
            "artifacts": artifacts_list,
            "risks": risks,
            "next_actions": next_actions
        }
        
        path.write_text(yaml.dump(packet, sort_keys=False), encoding="utf-8")
        
        events.append_event(run_id, "delivery.updated", {"packet_id": packet["packet_id"]})
        events.append_event(run_id, "delivery.build.completed", {"status": status})
        
        rebuild_timeline_from_events(run_id)
        finalize_evidence_packet(run_id)
    except Exception as e:
        events.append_event(run_id, "delivery.build.failed", {"error": str(e)})
        rebuild_timeline_from_events(run_id)
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
