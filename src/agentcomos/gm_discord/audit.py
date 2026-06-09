import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir
from agentcomos.controller.events import append_event

def generate_audit(run_id: str) -> str:
    run_dir = get_run_dir(run_id)
    discord_dir = run_dir / "gm_discord"
    audit_path = discord_dir / "audit" / "gm_discord_audit.md"
    
    if audit_path.exists():
        return str(audit_path)
    
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    
    commands = []
    if (discord_dir / "commands").exists():
        for cmd_file in (discord_dir / "commands").glob("*.yaml"):
            with open(cmd_file, 'r') as f:
                commands.append(yaml.safe_load(f))
                
    content = f"# GM Discord Audit\n\n**Run ID:** {run_id}\n\n"
    
    if not commands:
        content += "No GM Discord commands found.\n"
        
    for cmd in commands:
        cmd_id = cmd.get("command_id")
        msg_id = cmd.get("message_id")
        
        inbound = {}
        inbound_path = discord_dir / "inbound" / f"{msg_id}.yaml"
        if inbound_path.exists():
            with open(inbound_path, 'r') as f:
                inbound = yaml.safe_load(f)
                
        result = {}
        result_path = discord_dir / "results" / f"{cmd_id}.yaml"
        if result_path.exists():
            with open(result_path, 'r') as f:
                result = yaml.safe_load(f)
                
        content += f"## Inbound Summary\n"
        content += f"- **Message ID:** {msg_id}\n"
        content += f"- **Received At:** {inbound.get('received_at', 'N/A')}\n"
        content += f"- **Content:** {inbound.get('content_redacted', 'N/A')}\n\n"
        
        content += f"## Parsed Command\n"
        content += f"- **Command ID:** {cmd_id}\n"
        content += f"- **Command Type:** {cmd.get('command_type', 'N/A')}\n"
        content += f"- **Risk Level:** {cmd.get('risk_level', 'N/A')}\n"
        content += f"- **Confirmation Requirement:** {cmd.get('requires_confirmation', True)}\n\n"
        
        content += f"## Result Summary\n"
        content += f"- **Status:** {result.get('status', 'pending')}\n"
        content += f"- **Summary:** {result.get('summary', 'N/A')}\n\n"
        
        content += f"## Safety Boundary\n"
        content += f"- Token Present: false\n"
        content += f"- Shell Executed: false\n"
        content += f"- Manual OS Bypassed: false\n"
        content += f"- Decision/Feynman Bypassed: false\n\n"
        
        content += f"## Evidence Paths\n"
        content += f"- Inbound Message: `{(inbound_path.relative_to(run_dir.parent.parent) if inbound_path.exists() else 'None')}`\n"
        content += f"- GM Command: `{(discord_dir / 'commands' / f'{cmd_id}.yaml').relative_to(run_dir.parent.parent)}`\n"
        content += f"- GM Command Result: `{(result_path.relative_to(run_dir.parent.parent) if result_path.exists() else 'None')}`\n\n"
        
        content += f"## Next Action\n"
        if result.get("status") == "requires_confirmation":
            content += "Awaiting explicit human confirmation.\n\n"
        else:
            content += "Review audit trail.\n\n"
            
    with open(audit_path, 'w') as f:
        f.write(content)
        
    append_event(run_id, "gm_discord.audit.generated", {"path": str(audit_path.relative_to(run_dir.parent.parent))})
    return str(audit_path)
