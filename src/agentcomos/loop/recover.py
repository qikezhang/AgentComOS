import yaml
from pathlib import Path

def recover_loop_status(run_id: str) -> dict:
    run_dir = Path(f".agentcomos/runs/{run_id}")
    trace_path = run_dir / "loop_trace.yaml"
    plan_path = run_dir / "loop_plan.yaml"
    
    if not trace_path.exists():
        raise ValueError(f"Cannot recover: loop_trace.yaml missing for run {run_id}")
    if not plan_path.exists():
        raise ValueError(f"Cannot recover: loop_plan.yaml missing for run {run_id}")
        
    trace = yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    
    ticks_executed = len(trace.get("ticks", []))
    tasks_advanced = sum(1 for t in trace.get("ticks", []) if t.get("advanced_task_id"))
    
    last_tick = trace.get("ticks", [])[-1] if trace.get("ticks") else None
    
    status = {
        "loop_id": f"LOOP-{run_id}",
        "run_id": run_id,
        "status": "partial",
        "runtime_mode": "fake",
        "ticks_requested": plan.get("max_ticks", 3),
        "ticks_executed": ticks_executed,
        "tasks_advanced": tasks_advanced,
        "stop_reason": "none",
        "real_runtime_used": False,
        "latest_tick": {
            "tick_number": last_tick["tick_number"] if last_tick else 0,
            "result": last_tick["result"] if last_tick else "none"
        },
        "blocked_on": {
            "type": "none",
            "task_id": None
        }
    }
    
    if last_tick:
        if last_tick["result"] == "no_ready_task":
            status["stop_reason"] = "no_ready_task"
            status["status"] = "completed"
        # We don't have full blocker state from trace alone easily without reading frontier,
        # but let's just do a basic recovery and if it's still blocked, next run will catch it.
        # So we'll leave it as partial unless no_ready_task.
    
    status_path = run_dir / "loop_status.yaml"
    status_path.write_text(yaml.dump(status, sort_keys=False), encoding="utf-8")
    return status
