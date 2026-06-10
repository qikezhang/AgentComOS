from agentcomos.adapters.docker_adapter import DockerAdapter
from agentcomos.executor_request import ExecutorRequest

def test_docker_adapter():
    adapter = DockerAdapter()
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    is_valid, reason, _ = adapter.validate_request(req, {})
    assert not is_valid
