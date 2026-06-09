import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.manual_os.request import get_manual_os_dir
from agentcomos.controller.events import append_event
from agentcomos.manual_os.models import ManualOsResult

def report_result(run_id: str, task_id: str, status: str, executed_by: str, summary: str) -> ManualOsResult:
    if not get_run_dir(run_id).exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    out_dir = get_manual_os_dir(run_id, task_id)
    req_file = out_dir / "manual_os_request.yaml"
    if not req_file.exists():
        raise ValueError(f"Manual OS request for {task_id} does not exist.")
        
    if status == "completed":
        app_file = out_dir / "manual_os_approval.yaml"
        if not app_file.exists():
            raise ValueError("Cannot complete manual OS task without prior approval.")
        with open(app_file, "r", encoding="utf-8") as f:
            app_data = yaml.safe_load(f)
            if not app_data or app_data.get("status") != "approved":
                raise ValueError("Cannot complete manual OS task without prior approval.")
                
    if not executed_by or not summary:
        raise ValueError("executed_by and summary cannot be empty.")
        
    res_file = out_dir / "manual_os_result.yaml"
    if res_file.exists():
        with open(res_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and data.get("status") == status:
                return ManualOsResult(**data)
                
    result = ManualOsResult(
        run_id=run_id,
        task_id=task_id,
        status=status,
        executed_by=executed_by,
        summary=summary
    )
    import dataclasses
    with open(res_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(dataclasses.asdict(result), f, sort_keys=False)
        
    append_event(run_id, "manual_os.result.reported", {"task_id": task_id, "status": status, "executed_by": executed_by})
    return result
