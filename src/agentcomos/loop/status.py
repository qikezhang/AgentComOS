import yaml
from pathlib import Path

def get_loop_status(run_id: str) -> dict:
    status_path = Path(f".agentcomos/runs/{run_id}/loop_status.yaml")
    plan_path = Path(f".agentcomos/runs/{run_id}/loop_plan.yaml")
    
    if not plan_path.exists():
        raise ValueError(f"Loop plan missing for run {run_id}")
        
    if not status_path.exists():
        return {
            "loop_id": f"LOOP-{run_id}",
            "run_id": run_id,
            "status": "active",
            "runtime_mode": "fake",
            "ticks_requested": 0,
            "ticks_executed": 0,
            "tasks_advanced": 0,
            "stop_reason": "none",
            "real_runtime_used": False,
            "latest_tick": {
                "tick_number": 0,
                "result": "none"
            },
            "blocked_on": {
                "type": "none",
                "task_id": None
            }
        }
        
    return yaml.safe_load(status_path.read_text(encoding="utf-8"))
