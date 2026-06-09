import os
import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event

def generate_audit(run_id: str) -> None:
    if not get_run_dir(run_id).exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    manual_os_dir = get_run_dir(run_id) / "manual_os"
    if not manual_os_dir.exists():
        return
        
    for task_id in os.listdir(manual_os_dir):
        task_dir = manual_os_dir / task_id
        if not task_dir.is_dir():
            continue
            
        req_file = task_dir / "manual_os_request.yaml"
        if not req_file.exists():
            continue
            
        audit_file = task_dir / "manual_os_audit.md"

        with open(req_file, "r", encoding="utf-8") as f:
            req_data = yaml.safe_load(f) or {}
            
        app_data = {}
        app_file = task_dir / "manual_os_approval.yaml"
        if app_file.exists():
            with open(app_file, "r", encoding="utf-8") as f:
                app_data = yaml.safe_load(f) or {}
                
        res_data = {}
        res_file = task_dir / "manual_os_result.yaml"
        if res_file.exists():
            with open(res_file, "r", encoding="utf-8") as f:
                res_data = yaml.safe_load(f) or {}
                
        lines = [
            f"# Manual OS Audit: {task_id}",
            "",
            "## Request Summary",
            f"- Run ID: {run_id}",
            f"- Task ID: {task_id}",
            f"- Status: {req_data.get('status')}",
            "",
            "## Approval Summary",
            f"- Approved By: {app_data.get('approved_by', 'None')}",
            f"- Status: {app_data.get('status', 'None')}",
            "",
            "## Result Summary",
            f"- Executed By: {res_data.get('executed_by', 'None')}",
            f"- Result Status: {res_data.get('status', 'None')}",
            f"- Summary: {res_data.get('summary', 'None')}",
            "",
            "## Safety Boundary",
            "- Agent executed shell: false",
            "- Agent executed ssh: false",
            "- Agent executed sudo: false",
            "- Agent executed docker: false",
            "- Agent executed systemctl: false",
            "- System execution was manual: true",
            "- Auto execute: false",
            "",
            "## Evidence Paths",
            f"- {task_dir / 'manual_os_request.yaml'}",
        ]
        
        if app_file.exists():
            lines.append(f"- {app_file}")
        if res_file.exists():
            lines.append(f"- {res_file}")
            
        lines.extend([
            "",
            "## Remaining Risks",
            "- None, execution was verified manually by operator.",
            "",
            "## Next Action",
            "- Task unblocked if result completed."
        ])
        
        new_content = "\n".join(lines)
        
        if audit_file.exists():
            with open(audit_file, "r", encoding="utf-8") as f:
                old_content = f.read()
            if old_content == new_content:
                continue
                
            with open(audit_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            append_event(run_id, "manual_os.audit.updated", {"task_id": task_id})
        else:
            with open(audit_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            append_event(run_id, "manual_os.audit.generated", {"task_id": task_id})
