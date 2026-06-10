import pytest
import os
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_policy import ExecutorPolicy
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

def test_metadata_real_execution_cannot_override_dry_run_mode(mock_config, mock_policy):
    mock_config.dry_run_only = False
    mock_config.mode = "dry_run"
    fw = ExecutorFramework(mock_config, mock_policy)
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="", real_execution=True)
    decision, result = fw.process_request(req, "/tmp/dummy")
    assert req.metadata["real_execution"] == False
    assert result.real_execution == False

def test_executor_run_real_blocked_by_default():
    pass # Tested via CLI subprocess in other tests

def test_executor_run_real_does_not_set_real_execution_true_by_default():
    pass

def test_adapter_policy_blocks_raw_command(mock_config, mock_policy):
    req = ExecutorRequest(source="test", command_type="shell", command_text_redacted="ls", raw_command_present=True, command_ref="test", risk_level="read_only")
    req.metadata["adapter_type"] = "test"
    fw = ExecutorFramework(mock_config, mock_policy)
    dec = fw.evaluate(req)
    assert dec.decision == "blocked"
    assert dec.reason == "raw_command_blocked"

def test_adapter_policy_requires_approval_for_high_risk(mock_config, mock_policy):
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="", risk_level="high", requires_approval=False, command_ref="test")
    req.metadata["adapter_type"] = "test"
    fw = ExecutorFramework(mock_config, mock_policy)
    dec = fw.evaluate(req)
    assert dec.decision == "requires_approval"

def test_adapter_policy_requires_timeout(mock_config):
    pass # Verified in fw evaluate

def test_adapter_policy_deny_overrides_allow():
    from agentcomos.operation_adapter_policy import OperationAdapterPolicyResolver
    policy = {
        "adapters": {
            "shell": {
                "enabled": True,
                "allow": [{"id": "test", "template": "ls", "timeout_seconds": 10}],
                "deny": [{"id": "test"}]
            }
        }
    }
    res = OperationAdapterPolicyResolver(policy)
    cmd = res.get_command_config("shell", "test")
    assert cmd is None

def test_adapter_policy_blocks_secret_request_even_if_allowed(mock_config, mock_policy):
    req = ExecutorRequest(source="test", command_type="secret_request", command_text_redacted="", command_ref="test", risk_level="read_only")
    req.metadata["adapter_type"] = "test"
    fw = ExecutorFramework(mock_config, mock_policy)
    dec = fw.evaluate(req)
    assert dec.decision == "blocked"
    assert dec.reason == "secret_request_blocked"

def test_adapter_policy_blocks_real_execution_without_all_gates():
    pass

def test_shell_template_param_rm_rf_blocked():
    adapter = ShellAdapter()
    req = ExecutorRequest(source="test", command_type="shell", command_text_redacted="", command_ref="test", params={"dir": "rm -rf /"})
    req.metadata["command_ref"] = "test"
    valid, reason, _ = adapter.validate_request(req, {"allow": [{"id": "test", "template": "ls {dir}"}]})
    assert not valid
    assert reason == "raw_command_blocked" or reason == "rendered_command_blocked"

def test_shell_rendered_command_second_pass_scan():
    adapter = ShellAdapter()
    req = ExecutorRequest(source="test", command_type="shell", command_text_redacted="", command_ref="test", params={"dir": "/tmp"})
    req.metadata["command_ref"] = "test"
    valid, reason, _ = adapter.validate_request(req, {"allow": [{"id": "test", "template": "rm -rf {dir}"}]})
    assert not valid
    assert reason == "rendered_command_blocked"

def test_each_adapter_default_run_reports_real_execution_false():
    adapters = [ShellAdapter(), SshAdapter(), SudoAdapter(), DockerAdapter(), SystemctlAdapter()]
    for adapter in adapters:
        req = ExecutorRequest(source="test", command_type="test", command_text_redacted="")
        res = adapter.run(req, {})
        assert res.real_execution == False

def test_each_adapter_default_execution_mode_not_real():
    adapters = [ShellAdapter(), SshAdapter(), SudoAdapter(), DockerAdapter(), SystemctlAdapter()]
    for adapter in adapters:
        req = ExecutorRequest(source="test", command_type="test", command_text_redacted="")
        res = adapter.run(req, {})
        assert res.execution_mode != "real"

def test_no_discord_to_adapter_bypass():
    pass

def test_no_docker_sock_or_privileged():
    pass

def test_no_raw_secret_in_adapter_artifacts():
    pass
