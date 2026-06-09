import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event
from agentcomos.gm_discord.models import GMCommand, SafetyCommand

def parse_message(run_id: str, message_id: str) -> str:
    run_dir = get_run_dir(run_id)
    inbound_path = run_dir / "gm_discord" / "inbound" / f"{message_id}.yaml"
    if not inbound_path.exists():
        raise ValueError(f"Inbound message not found: {message_id}")
        
    with open(inbound_path, 'r') as f:
        inbound = yaml.safe_load(f)
        
    content = inbound.get("content_redacted", "").strip()
    command_id = f"GMC-{message_id}"
    
    cmd_type = "unknown"
    read_only = False
    requires_conf = True
    risk_level = "high"
    status = "parsed"
    
    parts = content.split()
    cmd_word = parts[0].lower() if parts else ""
    
    # Simple router
    task_id = None
    max_ticks = None
    fake = None
    real_runtime_used = None
    reason = None
    
    if cmd_word in ["status", "report"]:
        cmd_type = cmd_word
        read_only = True
        requires_conf = False
        risk_level = "low"
    elif cmd_word == "approve" and len(parts) >= 2 and parts[1] == "manual-os":
        cmd_type = "manual_os_approve"
        risk_level = "medium"
    elif cmd_word == "reject" and len(parts) >= 2 and parts[1] == "manual-os":
        cmd_type = "manual_os_reject"
        risk_level = "medium"
    elif cmd_word == "result" and len(parts) >= 2 and parts[1] == "manual-os":
        cmd_type = "manual_os_result"
        risk_level = "medium"
    elif cmd_word == "decision" and len(parts) >= 4 and parts[1] == "result":
        cmd_type = "decision_result"
        task_id = parts[2]
        if task_id.startswith("task="):
            task_id = task_id.split("=")[1]
        decision = parts[3]
        if decision.startswith("decision="):
            decision = decision.split("=")[1]
        if decision not in ["approved", "rejected"]:
            status = "failed_parse"
            reason = "unsupported_decision"
        risk_level = "medium"
    elif cmd_word in ["approve", "reject"] and len(parts) >= 3 and parts[1] == "decision":
        cmd_type = "decision_result"
        task_id = parts[2]
        risk_level = "medium"
    elif cmd_word == "feynman" and len(parts) >= 4 and parts[1] == "result":
        cmd_type = "feynman_result"
        task_id = parts[2]
        if task_id.startswith("task="):
            task_id = task_id.split("=")[1]
        f_status = parts[3]
        if f_status.startswith("status="):
            f_status = f_status.split("=")[1]
        if f_status not in ["passed", "failed"]:
            status = "failed_parse"
            reason = "unsupported_feynman_status"
        risk_level = "medium"
    elif cmd_word in ["pass", "fail"] and len(parts) >= 3 and parts[1] == "feynman":
        cmd_type = "feynman_result"
        task_id = parts[2]
        risk_level = "medium"
    elif cmd_word == "loop" and len(parts) >= 2 and parts[1] == "run":
        cmd_type = "loop_run_request"
        risk_level = "medium"
        fake_val = False
        real_val = False
        for p in parts[2:]:
            if p.startswith("max_ticks="):
                try:
                    max_ticks = int(p.split("=")[1])
                except ValueError:
                    status = "blocked"
                    reason = "invalid_max_ticks"
            elif p in ["fake", "fake=true"]:
                fake_val = True
            elif p in ["real", "fake=false"]:
                real_val = True

        if status != "blocked":
            if max_ticks is None:
                status = "blocked"
                reason = "missing_max_ticks"
            elif not fake_val or real_val:
                status = "blocked"
                reason = "fake_required" if not real_val else "real_runtime_loop_forbidden"
            elif max_ticks > 10 or max_ticks < 1:
                status = "blocked"
                reason = "max_ticks_exceeds_g11_limit"
            else:
                fake = True
                real_runtime_used = False
    elif cmd_word == "run" and len(parts) >= 2 and parts[1].startswith("shell"):
        cmd_type = "shell"
        status = "blocked"
        risk_level = "high"
        reason = "prohibited_shell_command"
        requires_conf = True
    elif cmd_word in ["sudo", "systemctl", "docker", "ssh", "rm"]:
        cmd_type = "prohibited_command"
        status = "blocked"
        risk_level = "high"
        requires_conf = True
        if cmd_word == "sudo": reason = "sudo_command_blocked"
        elif cmd_word == "systemctl": reason = "systemctl_command_blocked"
        elif cmd_word == "docker": reason = "docker_command_blocked"
        elif cmd_word == "ssh": reason = "ssh_command_blocked"
        elif cmd_word == "rm": reason = "destructive_command_blocked"
    else:
        status = "blocked"
        reason = "unsupported_command"
        
    cmd = GMCommand(
        command_id=command_id,
        message_id=message_id,
        run_id=run_id,
        command_type=cmd_type,
        status=status,
        requires_confirmation=requires_conf,
        risk_level=risk_level,
        task_id=task_id,
        max_ticks=max_ticks,
        fake=fake,
        real_runtime_used=real_runtime_used,
        reason=reason,
        safety=SafetyCommand(
            read_only=read_only,
            requires_explicit_confirmation=requires_conf,
            bounded_loop=True if fake else False,
            real_runtime_used=False
        )
    )
    
    artifact_path = run_dir / "gm_discord" / "commands" / f"{command_id}.yaml"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(artifact_path, 'w') as f:
        yaml.safe_dump(cmd.model_dump(), f, sort_keys=False)
        
    event_type = "gm_discord.command.requires_confirmation" if requires_conf and status != "blocked" else "gm_discord.command.parsed"
    if status == "blocked":
        event_type = "gm_discord.command.blocked"
        
    append_event(run_id, event_type, {
        "command_id": command_id,
        "type": cmd_type,
        "path": str(artifact_path.relative_to(run_dir.parent.parent))
    })
    
    return str(artifact_path)
