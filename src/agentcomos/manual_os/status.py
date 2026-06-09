import os
import yaml
from agentcomos.controller.state import get_run_dir

def get_manual_os_status(run_id: str) -> dict:
    run_dir = get_run_dir(run_id)
    manual_os_dir = run_dir / "manual_os"
    if not manual_os_dir.exists():
        return {}
        
    results = {}
    for task_id in os.listdir(manual_os_dir):
        task_dir = manual_os_dir / task_id
        if not task_dir.is_dir():
            continue
            
        task_status = {
            "request": None,
            "approval": None,
            "result": None
        }
        
        req_file = task_dir / "manual_os_request.yaml"
        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                task_status["request"] = yaml.safe_load(f).get("status")
                
        app_file = task_dir / "manual_os_approval.yaml"
        if app_file.exists():
            with open(app_file, "r", encoding="utf-8") as f:
                task_status["approval"] = yaml.safe_load(f).get("status")
                
        res_file = task_dir / "manual_os_result.yaml"
        if res_file.exists():
            with open(res_file, "r", encoding="utf-8") as f:
                task_status["result"] = yaml.safe_load(f).get("status")
                
        results[task_id] = task_status
        
    return results
