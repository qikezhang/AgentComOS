import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event
from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.frontier.builder import read_task_frontier

def check_feynman(run_id: str, task_id: str, mode: str) -> None:
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
        
    feynman_dir = run_dir / "feynman" / task_id
    feynman_dir.mkdir(parents=True, exist_ok=True)
    
    result_path = feynman_dir / "feynman_result.yaml"
    if result_path.exists():
        return
        
    check_path = feynman_dir / "feynman_check.yaml"
    if not check_path.exists():
        req_data = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": mode,
            "created_by": "controller",
            "status": "requested",
            "source": "task_frontier",
            "check_type": "task_understanding",
            "question": "Can this task be explained clearly enough to execute safely?"
        }
        check_path.write_text(yaml.dump(req_data, sort_keys=False), encoding="utf-8")
        append_event(run_id, "feynman.check.started", {"task_id": task_id, "mode": mode})
        
    if not result_path.exists():
        res_data = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": mode,
            "status": "completed",
            "created_by": "controller",
            "real_runtime_used": False,
            "original_task": "...",
            "explanation": "Deterministic Feynman-style explanation generated for explicit G8 adoption.",
            "detected_ambiguities": [],
            "missing_inputs": [],
            "execution_risks": [
                {"id": "RISK-G8-FEYNMAN-001", "severity": "low", "summary": "This is a deterministic check, not a real LLM critique."}
            ],
            "pass": True
        }
        result_path.write_text(yaml.dump(res_data, sort_keys=False), encoding="utf-8")
        append_event(run_id, "feynman.check.completed", {"task_id": task_id, "pass": True})
        
    rebuild_timeline_from_events(run_id)
