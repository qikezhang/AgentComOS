from agentcomos.adapters.systemctl_adapter import SystemctlAdapter
from agentcomos.executor_request import ExecutorRequest

def test_systemctl_adapter():
    adapter = SystemctlAdapter()
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
    assert reason == "missing_command_ref"
    
    req.metadata["command_ref"] = "status"
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
    assert reason == "missing_service_ref"
    
    req.metadata["service_ref"] = "nginx"
    is_valid, reason, _ = adapter.validate_request(req, {"allowed_services": ["nginx"], "allowed_actions": ["status"]})
    assert is_valid
