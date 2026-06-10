import pytest
from pathlib import Path

def test_no_shell_commands_in_source():
    src_dir = Path("src/agentcomos")
    assert src_dir.exists()
    
    forbidden_terms = [
        "subprocess.", "os.system(", "paramiko.", "ssh ", "sudo ",
        "systemctl ", "docker compose restart", "docker run",
        "/var/run/docker.sock"
    ]
    
    # We only check discord adapter files for these boundaries
    discord_files = list(src_dir.glob("discord_*.py"))
    
    for df in discord_files:
        content = df.read_text()
        for term in forbidden_terms:
            assert term not in content, f"Forbidden term {term} found in {df}"

def test_no_executor_implementation():
    src_dir = Path("src/agentcomos")
    forbidden_classes = [
        "ControlledExecutor", "executor_policy", "executor_command",
        "operation_adapter", "systemctl_adapter", "docker_adapter"
    ]
    
    discord_files = list(src_dir.glob("discord_*.py"))
    for df in discord_files:
        content = df.read_text()
        for term in forbidden_classes:
            assert term not in content, f"R4/R5 implementation {term} found in {df}"
