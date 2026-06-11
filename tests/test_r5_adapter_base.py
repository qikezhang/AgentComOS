from agentcomos.operation_adapter_base import OperationAdapterBase
from agentcomos.executor_request import ExecutorRequest

def test_base_adapter():
    adapter = OperationAdapterBase()
    assert adapter.adapter_type == "unknown"
    assert adapter.enabled == False
    
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
    assert reason == "Not implemented"
    
    res = adapter.dry_run(req, {})
    assert res.status == "blocked"
