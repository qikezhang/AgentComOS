import yaml
from pathlib import Path
from agentcomos.program.builder import validate_run_exists

def create_loop_plan(run_id: str) -> dict:
    validate_run_exists(run_id)
    run_dir = Path(f".agentcomos/runs/{run_id}")
    plan_path = run_dir / "loop_plan.yaml"
    
    if plan_path.exists():
        return yaml.safe_load(plan_path.read_text(encoding="utf-8"))
        
    plan_data = {
        "loop_id": f"LOOP-{run_id}",
        "run_id": run_id,
        "created_by": "controller",
        "status": "active",
        "runtime_mode": "fake",
        "max_ticks": 3,
        "max_task_advancements": 3,
        "stop_conditions": [
            "no_ready_task",
            "awaiting_decision",
            "awaiting_feynman",
            "failed_task",
            "max_ticks_reached",
            "max_task_advancements_reached"
        ],
        "constraints": {
            "fake_runtime_only": True,
            "no_real_opencode": True,
            "no_real_hermes": True,
            "no_discord": True,
            "no_recursive_task_expansion": True,
            "no_worker_evolution": True,
            "no_manual_os": True,
            "no_auto_versioner": True,
            "no_automatic_decision_market": True,
            "no_automatic_feynman_executor": True
        }
    }
    
    plan_path.write_text(yaml.dump(plan_data, sort_keys=False), encoding="utf-8")
    return plan_data

def read_loop_plan(run_id: str) -> dict | None:
    plan_path = Path(f".agentcomos/runs/{run_id}/loop_plan.yaml")
    if not plan_path.exists():
        return None
    return yaml.safe_load(plan_path.read_text(encoding="utf-8"))
