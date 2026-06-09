import yaml
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event
from agentcomos.gm_discord.models import GMCommandResult, SafetyCommandResult
from agentcomos.controller.runner import handle_run_status
from agentcomos.gm.report import generate_gm_report
from agentcomos.manual_os.approval import approve_request, reject_request
from agentcomos.manual_os.result import report_result
from agentcomos.decision.status import get_decision_result
from agentcomos.feynman.status import get_feynman_result
from agentcomos.loop.runner import run_loop

def execute_command(run_id: str, command_id: str, confirm: str = None) -> str:
    run_dir = get_run_dir(run_id)
    cmd_path = run_dir / "gm_discord" / "commands" / f"{command_id}.yaml"
    if not cmd_path.exists():
        raise ValueError(f"Command not found: {command_id}")
        
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
        
    if cmd["status"] == "blocked":
        return _write_result(run_id, command_id, "blocked", "Command is blocked for safety.", cmd)
        
    if cmd["requires_confirmation"] and confirm != "explicit":
        return _write_result(run_id, command_id, "requires_confirmation", "Command requires explicit confirmation.", cmd)
        
    msg_id = cmd["message_id"]
    inbound_path = run_dir / "gm_discord" / "inbound" / f"{msg_id}.yaml"
    content = ""
    if inbound_path.exists():
        with open(inbound_path, 'r') as f:
            content = yaml.safe_load(f).get("content_redacted", "").strip()
            
    parts = content.split()
    cmd_type = cmd["command_type"]
    
    try:
        if cmd_type == "status":
            handle_run_status(run_id)
            summary = "Status checked."
            
        elif cmd_type == "report":
            generate_gm_report(run_id, format="markdown")
            summary = "GM report generated."
            
        elif cmd_type == "manual_os_approve":
            task = parts[2] if len(parts) > 2 else "UNKNOWN"
            approve_request(run_id, task, "GM Discord Bridge")
            summary = f"Approved manual_os for {task}."
            
        elif cmd_type == "manual_os_reject":
            task = parts[2] if len(parts) > 2 else "UNKNOWN"
            reason = " ".join(parts[3:]) if len(parts) > 3 else "Rejected via Discord"
            reject_request(run_id, task, "GM Discord Bridge", reason)
            summary = f"Rejected manual_os for {task}."
            
        elif cmd_type == "manual_os_result":
            task = parts[2] if len(parts) > 2 else "UNKNOWN"
            status = parts[3] if len(parts) > 3 else "completed"
            summary_text = " ".join(parts[4:]) if len(parts) > 4 else "Completed via Discord"
            report_result(run_id, task, status, "GM Discord Bridge", summary_text)
            summary = f"Reported manual_os result for {task}."
            
        elif cmd_type == "decision_result":
            task = parts[2] if len(parts) > 2 else "UNKNOWN"
            get_decision_result(run_id, task)
            summary = f"Generated decision result for {task}."
            
        elif cmd_type == "feynman_result":
            task = parts[2] if len(parts) > 2 else "UNKNOWN"
            get_feynman_result(run_id, task)
            summary = f"Generated feynman result for {task}."
            
        elif cmd_type == "loop_run_request":
            max_ticks = 0
            for p in parts:
                if p.startswith("max_ticks="):
                    max_ticks = int(p.split("=")[1])
            if max_ticks <= 0:
                raise ValueError("max_ticks must be provided and > 0")
            if "fake" not in parts:
                raise ValueError("loop run must be fake via Discord")
            run_loop(run_id, max_ticks, fake=True)
            summary = f"Executed fake loop run with max_ticks={max_ticks}."
            
        else:
            return _write_result(run_id, command_id, "blocked", f"Unknown command type: {cmd_type}", cmd)
            
        return _write_result(run_id, command_id, "completed", summary, cmd)
    except Exception as e:
        return _write_result(run_id, command_id, "failed", str(e), cmd)


def _write_result(run_id: str, command_id: str, status: str, summary: str, cmd: dict) -> str:
    run_dir = get_run_dir(run_id)
    result_path = run_dir / "gm_discord" / "results" / f"{command_id}.yaml"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = GMCommandResult(
        command_id=command_id,
        status=status,
        summary=summary,
        safety=SafetyCommandResult(
            auto_execute=False,
            shell_executed=False,
            manual_os_bypassed=False,
            decision_feynman_bypassed=False
        )
    )
    
    with open(result_path, 'w') as f:
        yaml.safe_dump(result.model_dump(), f, sort_keys=False)
        
    if status == "completed":
        append_event(run_id, "gm_discord.command.executed", {"command_id": command_id, "summary": summary})
    elif status == "blocked":
        append_event(run_id, "gm_discord.command.blocked", {"command_id": command_id, "reason": summary})
        
    return str(result_path)
