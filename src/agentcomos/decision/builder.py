import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event
from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.frontier.builder import read_task_frontier

def request_decision(run_id: str, task_id: str, mode: str) -> None:
    if mode != "explicit":
        raise ValueError("mode must be 'explicit'")
        
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} not found")
        
    frontier = read_task_frontier(run_id)
    if not frontier:
        raise ValueError(f"Task frontier not found for run {run_id}")
        
    tasks = [t["task_id"] for t in frontier.get("tasks", [])]
    if task_id not in tasks:
        raise ValueError(f"Task {task_id} not found in frontier")
        
    decision_dir = run_dir / "decision" / task_id
    decision_dir.mkdir(parents=True, exist_ok=True)
    
    result_path = decision_dir / "decision_result.yaml"
    if result_path.exists():
        return
        
    request_path = decision_dir / "decision_request.yaml"
    if not request_path.exists():
        req_data = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": mode,
            "created_by": "controller",
            "status": "requested",
            "source": "task_frontier",
            "criteria": ["feasibility", "safety", "evidence"],
            "options": [
                {"option_id": "option_a", "summary": "Proceed with current task plan"},
                {"option_id": "option_b", "summary": "Block task until additional evidence exists"}
            ]
        }
        request_path.write_text(yaml.dump(req_data, sort_keys=False), encoding="utf-8")
        append_event(run_id, "decision.requested", {"task_id": task_id, "mode": mode})
        
    if not result_path.exists():
        res_data = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": mode,
            "status": "completed",
            "created_by": "controller",
            "real_runtime_used": False,
            "options": [
                {"option_id": "option_a", "score": 0.7},
                {"option_id": "option_b", "score": 0.3}
            ],
            "selected_option": "option_a",
            "rationale": "Controlled deterministic decision result generated for explicit G8 adoption.",
            "risks": [
                {"id": "RISK-G8-DECISION-001", "severity": "low", "summary": "Decision is deterministic and not a real multi-agent market."}
            ]
        }
        result_path.write_text(yaml.dump(res_data, sort_keys=False), encoding="utf-8")
        append_event(run_id, "decision.completed", {"task_id": task_id, "selected_option": "option_a"})
        
    rebuild_timeline_from_events(run_id)
