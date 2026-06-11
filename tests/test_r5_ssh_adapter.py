from agentcomos.adapters.ssh_adapter import SshAdapter
from agentcomos.executor_request import ExecutorRequest

def test_ssh_adapter():
    adapter = SshAdapter()
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
