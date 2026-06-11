import pytest
import os
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_config import ExecutorConfig
from agentcomos.adapters.shell_adapter import ShellAdapter
from agentcomos.adapters.ssh_adapter import SshAdapter
from agentcomos.adapters.sudo_adapter import SudoAdapter
from agentcomos.adapters.docker_adapter import DockerAdapter
from agentcomos.adapters.systemctl_adapter import SystemctlAdapter

@pytest.fixture
def mock_config():
    config = ExecutorConfig()
    config.enabled = True
    config.mode = "dry_run"
    config.dry_run_only = True
    config.require_approval_for_high_risk = True
    return config

@pytest.fixture
def mock_policy():
    class DummyPolicy:
        policy_id = "test_policy"
        def is_source_allowed(self, source):
            return True
        def get_raw_dict(self):
            return {
                "adapters": {
                    "test": {"enabled": True, "allow": [{"id": "test", "timeout_seconds": 10}]}
                }
            }
    return DummyPolicy()

def test_metadata_real_execution_cannot_override_dry_run_only(mock_config, mock_policy):
    mock_config.dry_run_only = True
    fw = ExecutorFramework(mock_config, mock_policy)
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="", real_execution=True)
    decision, result = fw.process_request(req, "/tmp/dummy")
    assert req.metadata["real_execution"] == False
    assert result.real_execution == False
    assert decision.decision == "blocked" or decision.decision == "adapter_policy_missing"

def test_executor_run_real_blocked_by_default():
    adapter = ShellAdapter()
    req = ExecutorRequest(source="test", command_type="shell", command_text_redacted="ls", command_ref="test")
    res = adapter.run(req, {"allow": [{"id": "test", "template": "ls"}]})
    assert res.real_execution == False
    assert res.execution_mode == "mock"

def test_adapter_dry_run_existing_fixture_runs_without_constructor_error():
    adapter = SystemctlAdapter()
    req = ExecutorRequest(source="test", command_type="systemctl_command", command_text_redacted="", command_ref="systemctl_status")
    req.metadata["service_ref"] = "app"
    res = adapter.dry_run(req, {"allowed_services": ["app"], "allowed_actions": ["systemctl_status"]})
    assert res.status == "dry_run_completed"

def test_docker_system_prune_blocked_even_if_allowlisted():
    adapter = DockerAdapter()
    req = ExecutorRequest(source="test", command_type="docker_command", command_text_redacted="", command_ref="docker_system_prune")
    valid, reason, _ = adapter.validate_request(req, {"allow": [{"id": "docker_system_prune", "template": "docker system prune -af"}]})
    assert not valid
    assert reason == "destructive_docker_command_blocked"

def test_docker_privileged_run_blocked():
    adapter = DockerAdapter()
    req = ExecutorRequest(source="test", command_type="docker_command", command_text_redacted="", command_ref="docker_run_privileged")
    valid, reason, _ = adapter.validate_request(req, {"allow": [{"id": "docker_run_privileged", "template": "docker run --privileged ubuntu bash"}]})
    assert not valid
    assert reason == "destructive_docker_command_blocked"

def test_ssh_rendered_rm_rf_blocked_even_on_allowlisted_host():
    adapter = SshAdapter()
    req = ExecutorRequest(source="test", command_type="ssh_command", command_text_redacted="", command_ref="ssh_rmrf")
    req.metadata["host_ref"] = "host1"
    valid, reason, _ = adapter.validate_request(req, {"allowed_hosts": [{"host": "host1"}], "allow": [{"id": "ssh_rmrf", "template": "rm -rf /"}]})
    assert not valid
    assert reason == "rendered_command_blocked"

def test_systemctl_restart_requires_approval_even_if_request_low_risk():
    adapter = SystemctlAdapter()
    req = ExecutorRequest(source="test", command_type="systemctl_command", command_text_redacted="", command_ref="systemctl_restart", risk_level="read_only")
    req.metadata["service_ref"] = "app"
    req.metadata["approved"] = False
    valid, reason, _ = adapter.validate_request(req, {"allowed_services": ["app"], "allowed_actions": ["systemctl_restart"]})
    assert not valid
    assert reason == "privileged_approval_required"

def test_systemctl_stop_requires_approval_even_if_metadata_read_only():
    adapter = SystemctlAdapter()
    req = ExecutorRequest(source="test", command_type="systemctl_command", command_text_redacted="", command_ref="systemctl_stop")
    req.metadata["service_ref"] = "app"
    req.metadata["approved"] = False
    req.metadata["risk_level"] = "read_only"
    valid, reason, _ = adapter.validate_request(req, {"allowed_services": ["app"], "allowed_actions": ["systemctl_stop"]})
    assert not valid
    assert reason == "privileged_approval_required"

def test_sudo_allow_unapproved_cannot_bypass_approval():
    adapter = SudoAdapter()
    req = ExecutorRequest(source="test", command_type="sudo_command", command_text_redacted="", command_ref="sudo_ls_root")
    req.metadata["approved"] = False
    valid, reason, _ = adapter.validate_request(req, {"allow_unapproved": True, "allow": [{"id": "sudo_ls_root", "template": "sudo ls /root"}]})
    assert not valid
    assert reason == "invalid_policy_allow_unapproved"

def test_sudo_ls_root_requires_approval_even_if_allow_unapproved_true():
    adapter = SudoAdapter()
    req = ExecutorRequest(source="test", command_type="sudo_command", command_text_redacted="", command_ref="sudo_ls_root")
    req.metadata["approved"] = False
    valid, reason, _ = adapter.validate_request(req, {"allow_unapproved": True, "allow": [{"id": "sudo_ls_root", "template": "sudo ls /root"}]})
    assert not valid
    assert reason == "invalid_policy_allow_unapproved"

def test_adapter_status_reports_dry_run_mock_capability():
    adapter = ShellAdapter()
    assert getattr(adapter, "dry_run", None) is not None
    assert getattr(adapter, "run", None) is not None

def test_no_placeholder_blocker_tests():
    with open(__file__, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "test_no_placeholder_blocker_tests" in line:
            continue
        assert "assert " + "True" not in line
        assert "pass\n" not in line
        assert "TO" + "DO" not in line
        assert "place" + "holder" not in line

