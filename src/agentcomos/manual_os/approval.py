import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.manual_os.request import get_manual_os_dir
from agentcomos.controller.events import append_event
from agentcomos.manual_os.models import ManualOsApproval

def _check_request_exists(run_id: str, task_id: str) -> Path:
    if not get_run_dir(run_id).exists():
        raise ValueError(f"Run {run_id} does not exist.")
    req_file = get_manual_os_dir(run_id, task_id) / "manual_os_request.yaml"
    if not req_file.exists():
        raise ValueError(f"Manual OS request for {task_id} does not exist.")
    return req_file

def approve_request(run_id: str, task_id: str, approved_by: str) -> ManualOsApproval:
    if not approved_by:
        raise ValueError("approved_by cannot be empty.")
    _check_request_exists(run_id, task_id)
    out_dir = get_manual_os_dir(run_id, task_id)
    app_file = out_dir / "manual_os_approval.yaml"
    
    if app_file.exists():
        with open(app_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                current_status = data.get("status")
                if current_status == "approved":
                    return ManualOsApproval(**data)
                elif current_status == "rejected":
                    raise ValueError("manual_os decision already rejected and cannot be changed to approved")
                
    approval = ManualOsApproval(
        run_id=run_id,
        task_id=task_id,
        status="approved",
        approved_by=approved_by,
    )
    import dataclasses
    with open(app_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(dataclasses.asdict(approval), f, sort_keys=False)
        
    append_event(run_id, "manual_os.approved", {"task_id": task_id, "approved_by": approved_by})
    return approval

def reject_request(run_id: str, task_id: str, rejected_by: str, reason: str) -> ManualOsApproval:
    if not rejected_by or not reason:
        raise ValueError("rejected_by and reason cannot be empty.")
    _check_request_exists(run_id, task_id)
    out_dir = get_manual_os_dir(run_id, task_id)
    app_file = out_dir / "manual_os_approval.yaml"
    
    if app_file.exists():
        with open(app_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                current_status = data.get("status")
                if current_status == "rejected":
                    return ManualOsApproval(**data)
                elif current_status == "approved":
                    raise ValueError("manual_os decision already approved and cannot be changed to rejected")
                
    approval = ManualOsApproval(
        run_id=run_id,
        task_id=task_id,
        status="rejected",
        rejected_by=rejected_by,
        reason=reason
    )
    import dataclasses
    with open(app_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(dataclasses.asdict(approval), f, sort_keys=False)
        
    append_event(run_id, "manual_os.rejected", {"task_id": task_id, "rejected_by": rejected_by})
    return approval
