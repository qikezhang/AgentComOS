from agentcomos.adapters.sudo_adapter import SudoAdapter
from agentcomos.executor_request import ExecutorRequest

def test_sudo_adapter():
    adapter = SudoAdapter()
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
