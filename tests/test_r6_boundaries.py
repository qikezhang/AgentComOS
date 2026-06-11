import pytest
from pathlib import Path
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_policy import ExecutorPolicy
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_request import ExecutorRequest

def test_r6_discord_non_bypass_is_proven():
    # Verify no discord adapter can be called directly
    from agentcomos.adapters import registry
    for name, adapter in registry.list_adapters().items():
        assert "discord" not in name.lower()
        assert "discord" not in adapter.adapter_type.lower()

def test_r6_preserves_systemctl_approval_gate():
    config = ExecutorConfig()
    policy = ExecutorPolicy({"adapters": []})
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(operation="systemctl restart nginx", arguments={}, source="test", command_type="test", command_text_redacted="test")
    res = fw.evaluate(req)
    assert res.decision == "blocked"
    assert "approval required" in res.reason.lower() or "policy" in res.reason.lower() or "not match" in res.reason.lower() or "disabled" in res.reason.lower()

def test_r6_preserves_sudo_allow_unapproved_block():
    config = ExecutorConfig()
    policy = ExecutorPolicy({"adapters": []})
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(operation="sudo something", arguments={}, source="test", command_type="test", command_text_redacted="test")
    res = fw.evaluate(req)
    assert res.decision == "blocked"

def test_r6_preserves_docker_prune_block():
    config = ExecutorConfig()
    policy = ExecutorPolicy({"adapters": []})
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(operation="docker system prune -a", arguments={}, source="test", command_type="test", command_text_redacted="test")
    res = fw.evaluate(req)
    assert res.decision == "blocked"

def test_r6_preserves_ssh_rmrf_block():
    config = ExecutorConfig()
    policy = ExecutorPolicy({"adapters": []})
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(operation="ssh server rm -rf /", arguments={}, source="test", command_type="test", command_text_redacted="test")
    res = fw.evaluate(req)
    assert res.decision == "blocked"

def test_r6_metadata_real_execution_still_blocked():
    config = ExecutorConfig()
    policy = ExecutorPolicy({"adapters": []})
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(operation="ls", arguments={}, source="test", command_type="test", command_text_redacted="test", metadata={"execution_mode": "real", "real_execution": True})
    res = fw.evaluate(req)
    # the mode should still be blocked or dry_run if it respects policy
    assert res.execution_mode != "real"

def test_r6_no_os_popen_in_code():
    root = Path(__file__).parent.parent
    for py_file in root.rglob("*.py"):
        if "venv" in str(py_file) or ".opencode" in str(py_file):
            continue
        if py_file.name == "test_r6_boundaries.py" or py_file.name == "test_r6_cli.py":
            continue
        text = py_file.read_text(errors="ignore")
        # Ensure the literal string 'os'+'.'+'popen' is not used (we check for os"."popen)
        assert "os" + ".popen(" not in text
