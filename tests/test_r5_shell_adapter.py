from agentcomos.adapters.shell_adapter import ShellAdapter
from agentcomos.executor_request import ExecutorRequest

def test_shell_adapter():
    adapter = ShellAdapter()
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    
    # Missing command ref
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
    assert reason == "missing_command_ref"
    
    req.command_ref = "cmd1"
    
    # Not allowed
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
    assert reason == "command_not_allowed"
    
    # Allowed but missing template
    is_valid, reason, _ = adapter.validate_request(req, {"allow": [{"id": "cmd1"}]})
    assert not is_valid
    assert reason == "missing_template"
    
    # Valid
    is_valid, reason, rendered = adapter.validate_request(req, {"allow": [{"id": "cmd1", "template": "echo hello"}]})
    assert is_valid
    assert "echo hello" in rendered
    
    # Dry run
    res = adapter.dry_run(req, {"allow": [{"id": "cmd1", "template": "echo hello"}]})
    assert res.status == "dry_run_completed"
    assert not res.real_execution
    
    # No real execution
    res2 = adapter.run(req, {"allow": [{"id": "cmd1", "template": "echo hello"}]})
    assert res2.status == "mock_completed"
    assert not res2.real_execution
    assert "[MOCK-RUN]" in res2.stdout_redacted
