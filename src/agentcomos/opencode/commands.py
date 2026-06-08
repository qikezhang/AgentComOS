import shlex

def build_opencode_serve_command(hostname: str = "127.0.0.1", port: int = 4096) -> str:
    """Build the OpenCode serve command."""
    return f"opencode serve --hostname {hostname} --port {port}"

def build_opencode_run_attach_command(run_id: str, phase: str, server: str = "http://127.0.0.1:4096") -> str:
    """Build the OpenCode run --attach command."""
    cmd = [
        "opencode", "run", "--attach", server,
        "--agent", f"agentcomos-{phase}",
        "--dir", f".worktrees/{run_id}/opencode",
        "--title", f"{run_id} {phase}",
        "--format", "json",
        f"Read .agentcomos/runs/{run_id}/operating_intent.yaml and runtime_context_bundle.yaml. Execute .opencode/commands/accept-gm-intent.md.",
    ]
    return " ".join(shlex.quote(c) for c in cmd)
