import os
from unittest import mock
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_policy import ExecutorPolicy

@mock.patch.dict(os.environ, {
    "CONTROLLED_EXECUTOR_ENABLED": "true",
    "CONTROLLED_EXECUTOR_MODE": "dry_run", 
    "CONTROLLED_EXECUTOR_DEFAULT_DECISION": "allow"
})
def test_executor_integration(tmp_path):
    config = ExecutorConfig()
    policy = ExecutorPolicy({"policy_id": "policy1", "allowed_sources": ["test"]})
    # Missing adapter policy -> blocked
    fw = ExecutorFramework(config, policy)
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="echo test", risk_level="low", status="allowed")
    req.metadata["adapter_type"] = "shell"
    decision, result = fw.process_request(req, str(tmp_path))
    assert decision.decision == "adapter_policy_missing"
    assert result.status == "blocked"
