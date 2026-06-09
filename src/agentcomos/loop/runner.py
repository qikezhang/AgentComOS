import yaml
from pathlib import Path
from datetime import datetime, timezone
from agentcomos.controller.runner import handle_controller_tick
from agentcomos.controller.events import append_event
from agentcomos.frontier.builder import read_task_frontier

def run_loop(run_id: str, max_ticks: int, fake: bool) -> None:
    if not fake:
        raise ValueError("Loop execution currently only supports --fake runtime.")
    if max_ticks is None or max_ticks <= 0:
        raise ValueError("max_ticks must be a positive integer.")
    
    plan_path = Path(f".agentcomos/runs/{run_id}/loop_plan.yaml")
    if not plan_path.exists():
        raise ValueError("loop_plan.yaml is missing. Run `agentcomos loop plan` first.")
        
    status_path = Path(f".agentcomos/runs/{run_id}/loop_status.yaml")
    trace_path = Path(f".agentcomos/runs/{run_id}/loop_trace.yaml")
    summary_path = Path(f".agentcomos/runs/{run_id}/loop_summary.md")
    
    status = _get_or_create_status(run_id, max_ticks)
    trace = _get_or_create_trace(run_id)
    
    if status["status"] in ("completed", "failed"):
        return
        
    status["status"] = "running"
    
    append_event(run_id, "loop.started", {"max_ticks": max_ticks})
    
    stop_reason = "max_ticks_reached"
    
    for i in range(max_ticks):
        append_event(run_id, "loop.tick.started", {"tick_number": status["ticks_executed"] + 1})
        
        # Check blockers BEFORE tick
        frontier = read_task_frontier(run_id)
        if _is_blocked_on_decision_or_feynman(frontier, status):
            stop_reason = status["stop_reason"]
            append_event(run_id, "loop.tick.blocked", {"stop_reason": stop_reason})
            break
            
        g7_result = handle_controller_tick(run_id, fake=fake)
        
        # After tick, determine result
        tick_result = "task_completed" if g7_result and g7_result.get("status") == "advanced" else "completed"
        advanced_task_id = None
        if g7_result:
            if g7_result.get("status") == "advanced":
                advanced_task_id = g7_result.get("task_id")
                status["tasks_advanced"] += 1
            elif g7_result.get("status") == "no_op" and g7_result.get("reason") == "no_ready_task":
                tick_result = "no_ready_task"
                stop_reason = "no_ready_task"
            
        status["ticks_executed"] += 1
        
        now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        trace_entry = {
            "tick_number": status["ticks_executed"],
            "started_at": now_str,
            "result": tick_result,
            "advanced_task_id": advanced_task_id,
            "fake_runtime": True,
            "real_runtime_used": False
        }
        trace["ticks"].append(trace_entry)
        
        status["latest_tick"]["tick_number"] = status["ticks_executed"]
        status["latest_tick"]["result"] = tick_result
        
        append_event(run_id, "loop.tick.completed", {"tick_result": tick_result})
        
        # Check blockers AFTER tick
        frontier = read_task_frontier(run_id)
        if tick_result == "no_ready_task":
            break
        elif _is_blocked_on_decision_or_feynman(frontier, status):
            stop_reason = status["stop_reason"]
            break
        elif status["tasks_advanced"] >= yaml.safe_load(plan_path.read_text()).get("max_task_advancements", 999):
            stop_reason = "max_task_advancements_reached"
            break
            
    status["stop_reason"] = stop_reason
    if stop_reason == "max_ticks_reached":
        status["status"] = "partial" if status["tasks_advanced"] > 0 else "completed"
    elif stop_reason == "no_ready_task":
        status["status"] = "completed"
    elif stop_reason in ("awaiting_decision", "awaiting_feynman"):
        status["status"] = "blocked"
    elif stop_reason == "failed_task":
        status["status"] = "failed"
    else:
        status["status"] = "partial"
        
    _write_status(status_path, status)
    _write_trace(trace_path, trace)
    _write_summary(summary_path, status)
    
    append_event(run_id, "loop.stopped", {"stop_reason": stop_reason})
    if status["status"] == "completed":
        append_event(run_id, "loop.completed", {})

def _get_or_create_status(run_id: str, max_ticks: int) -> dict:
    status_path = Path(f".agentcomos/runs/{run_id}/loop_status.yaml")
    if status_path.exists():
        return yaml.safe_load(status_path.read_text(encoding="utf-8"))
    return {
        "loop_id": f"LOOP-{run_id}",
        "run_id": run_id,
        "status": "active",
        "runtime_mode": "fake",
        "ticks_requested": max_ticks,
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

def _get_or_create_trace(run_id: str) -> dict:
    trace_path = Path(f".agentcomos/runs/{run_id}/loop_trace.yaml")
    if trace_path.exists():
        return yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    return {
        "loop_id": f"LOOP-{run_id}",
        "run_id": run_id,
        "runtime_mode": "fake",
        "ticks": []
    }

def _write_status(path: Path, status: dict) -> None:
    path.write_text(yaml.dump(status, sort_keys=False), encoding="utf-8")

def _write_trace(path: Path, trace: dict) -> None:
    path.write_text(yaml.dump(trace, sort_keys=False), encoding="utf-8")

def _write_summary(path: Path, status: dict) -> None:
    summary = f"""# Loop Summary

- Run: {status['run_id']}
- Loop: {status['loop_id']}
- Runtime mode: fake
- Ticks requested: {status['ticks_requested']}
- Ticks executed: {status['ticks_executed']}
- Tasks advanced: {status['tasks_advanced']}
- Stop reason: {status['stop_reason']}
- Real runtime used: false
- Decision/Feynman auto trigger: disabled
- Manual OS: not enabled
- Worker Evolution: not enabled
- Auto Versioner: not enabled
"""
    path.write_text(summary, encoding="utf-8")

def _is_blocked_on_decision_or_feynman(frontier: dict, status: dict) -> bool:
    if not frontier or "tasks" not in frontier:
        return False
        
    for task in frontier["tasks"]:
        if task["status"] == "failed":
            status["blocked_on"] = {"type": "failed_task", "task_id": task["task_id"]}
            status["stop_reason"] = "failed_task"
            return True
            
        if task["status"] == "blocked":
            if task.get("decision_required"):
                status["blocked_on"] = {"type": "decision", "task_id": task["task_id"]}
                status["stop_reason"] = "awaiting_decision"
                return True
            if task.get("feynman_required"):
                status["blocked_on"] = {"type": "feynman", "task_id": task["task_id"]}
                status["stop_reason"] = "awaiting_feynman"
                return True
                
    return False
