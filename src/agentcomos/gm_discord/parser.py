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
    elif cmd_word == "result" and len(parts) >= 2 and parts[1] == "decision":
        cmd_type = "decision_result"
        risk_level = "medium"
    elif cmd_word == "result" and len(parts) >= 2 and parts[1] == "feynman":
        cmd_type = "feynman_result"
        risk_level = "medium"
    elif cmd_word == "loop" and len(parts) >= 2 and parts[1] == "run":
        cmd_type = "loop_run_request"
        risk_level = "high"
        # Must have max_ticks and fake, validated in executor but noted here
    elif cmd_word == "run" and len(parts) >= 2 and parts[1] == "shell:":
        cmd_type = "shell"
        status = "blocked"
        risk_level = "high"
        requires_conf = True # Blocked anyway
    else:
        status = "blocked"
        
    cmd = GMCommand(
        command_id=command_id,
        message_id=message_id,
        run_id=run_id,
        command_type=cmd_type,
        status=status,
        requires_confirmation=requires_conf,
        risk_level=risk_level,
        safety=SafetyCommand(
            read_only=read_only,
            requires_explicit_confirmation=requires_conf
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
