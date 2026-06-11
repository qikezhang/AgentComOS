from pathlib import Path
import os
import re

def check_release_readiness() -> dict:
    blockers = []
    warnings = []
    
    root_dir = Path.cwd()
    
    # 1. R2 Docker production baseline present
    if not (root_dir / "Dockerfile").exists():
        blockers.append("Dockerfile missing")
    if not (root_dir / "docker-compose.yml").exists():
        blockers.append("docker-compose.yml missing")
    if not (root_dir / ".env.example").exists():
        blockers.append(".env.example missing")
        
    # 2. R3 Discord bot adapter present
    if not (root_dir / "src/agentcomos/discord_adapter.py").exists() and not (root_dir / "src/agentcomos/discord_runtime.py").exists():
        blockers.append("R3 Discord adapter missing")
        
    # 3. R4 Controlled Executor present
    if not (root_dir / "src/agentcomos/executor_framework.py").exists():
        blockers.append("R4 Controlled Executor missing")
        
    # 4. R5 Operation Adapters present
    if not (root_dir / "src/agentcomos/operation_adapter_base.py").exists():
        blockers.append("R5 Operation Adapters missing")
        
    # 5. Acceptance reports R2/R3/R4/R5 exist and passed
    for r in ["R2_DOCKER_PRODUCTION_SERVICE", "R3_REAL_DISCORD_BOT_ADAPTER", "R4_CONTROLLED_EXECUTOR_FRAMEWORK", "R5_OPERATION_ADAPTERS"]:
        report_path = root_dir / f"codex/acceptance-reports/{r}.md"
        if not report_path.exists():
            blockers.append(f"{r} acceptance report missing")
        else:
            content = report_path.read_text()
            if "Status: passed" not in content and "**Status:** passed" not in content:
                blockers.append(f"{r} acceptance report not passed")

    # 6. Check tracked files via git (approximate in python)
    # We will just check if .env or uv.lock exists and is tracked. 
    # Actually, simpler to just check if .env exists locally (it shouldn't be tracked) 
    # But .env is allowed locally, just not tracked. The instructions say "no .env tracked".
    # For testing, we can run git command.
    try:
        git_ls = os.popen("git ls-files").read().split()
        if ".env" in git_ls:
            blockers.append(".env is tracked")
        if "uv.lock" in git_ls:
            blockers.append("uv.lock is tracked")
        runs_tracked = [f for f in git_ls if f.startswith(".agentcomos/runs")]
        if runs_tracked:
            blockers.append(".agentcomos/runs is tracked")
    except Exception:
        warnings.append("Could not run git to check tracked files")

    # 7. Check docker.sock and privileged in compose
    compose_path = root_dir / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        if "docker.sock" in content or "/var/run/docker.sock" in content:
            blockers.append("docker.sock mount found in docker-compose.yml")
        if "privileged: true" in content:
            blockers.append("privileged container found in docker-compose.yml")
            
    # 8. Real secrets
    # simplistic scan
    # Check .env.example
    env_example = root_dir / ".env.example"
    if env_example.exists():
        content = env_example.read_text()
        if re.search(r"DISCORD_BOT_TOKEN=(?!replace-with-deployment-secret)[a-zA-Z0-9_-]+", content):
            blockers.append("Real secret found in .env.example")
            
    # 9. Release docs present
    if not (root_dir / "docs/releases/v2.8/06_OPERATOR_RUNBOOK.md").exists():
        blockers.append("Operator runbook missing")
    if not (root_dir / "docs/releases/v2.8/05_DEPLOYMENT_RUNBOOK.md").exists() and not (root_dir / "docs/releases/v2.8/rollback_plan.md").exists():
        warnings.append("Rollback notes missing")

    status = "pass" if not blockers else "fail"
    return {
        "status": status,
        "blockers": blockers,
        "warnings": warnings
    }
