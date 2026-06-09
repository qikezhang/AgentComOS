import yaml
from agentcomos.controller.state import get_run_dir

def get_decision_status(run_id: str) -> dict:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} not found")
        
    decision_dir = run_dir / "decision"
    decisions = {}
    if decision_dir.exists():
        for task_dir in decision_dir.iterdir():
            if task_dir.is_dir():
                task_id = task_dir.name
                res_path = task_dir / "decision_result.yaml"
                if res_path.exists():
                    data = yaml.safe_load(res_path.read_text(encoding="utf-8"))
                    decisions[task_id] = data.get("status", "unknown")
                else:
                    req_path = task_dir / "decision_request.yaml"
                    if req_path.exists():
                        decisions[task_id] = "requested"
    return {"run_id": run_id, "decisions": decisions}

def get_decision_result(run_id: str, task_id: str) -> dict:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} not found")
        
    res_path = run_dir / "decision" / task_id / "decision_result.yaml"
    if not res_path.exists():
        raise ValueError(f"Decision result not found for task {task_id}")
        
    return yaml.safe_load(res_path.read_text(encoding="utf-8"))
