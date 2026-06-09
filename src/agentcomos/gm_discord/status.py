from agentcomos.controller.state import get_run_dir

def get_gm_discord_status(run_id: str) -> dict:
    run_dir = get_run_dir(run_id)
    discord_dir = run_dir / "gm_discord"
    if not discord_dir.exists():
        return {"status": "inactive", "message": "No GM/Discord activity found."}
    
    inbound_count = len(list((discord_dir / "inbound").glob("*.yaml"))) if (discord_dir / "inbound").exists() else 0
    commands_count = len(list((discord_dir / "commands").glob("*.yaml"))) if (discord_dir / "commands").exists() else 0
    results_count = len(list((discord_dir / "results").glob("*.yaml"))) if (discord_dir / "results").exists() else 0
    outbound_count = len(list((discord_dir / "outbound").glob("*.yaml"))) if (discord_dir / "outbound").exists() else 0
    
    return {
        "status": "active",
        "inbound_messages": inbound_count,
        "commands_parsed": commands_count,
        "results": results_count,
        "outbound_messages": outbound_count,
    }
