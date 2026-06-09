import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event
from agentcomos.manual_os.models import ManualOsRequest, RequestedAction

def get_manual_os_dir(run_id: str, task_id: str) -> Path:
    return get_run_dir(run_id) / "manual_os" / task_id

def create_request(run_id: str, task_id: str) -> ManualOsRequest:
    if not get_run_dir(run_id).exists():
        raise ValueError(f"Run {run_id} does not exist.")
    
    # Check if task exists in frontier
    status_path = get_run_dir(run_id) / "task_frontier.yaml"
    if not status_path.exists():
        raise ValueError(f"Task frontier for {run_id} does not exist.")
        
    with open(status_path, "r", encoding="utf-8") as f:
        frontier = yaml.safe_load(f)
        
    task_found = False
    for task in frontier.get("tasks", []):
        if task.get("task_id") == task_id:
            task_found = True
            break
            
    if not task_found:
        raise ValueError(f"Task {task_id} not found in frontier.")
        
    out_dir = get_manual_os_dir(run_id, task_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    request_path = out_dir / "manual_os_request.yaml"
    
    if request_path.exists():
        with open(request_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            req = ManualOsRequest(**data)
            req.status = "already_current"
            return req
            
    req = ManualOsRequest(run_id=run_id, task_id=task_id, requested_action=RequestedAction(title=f"Manual OS Action for {task_id}"))
    
    import dataclasses
    with open(request_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(dataclasses.asdict(req), f, sort_keys=False)
        
    append_event(run_id, "manual_os.requested", {"task_id": task_id})
    return req
