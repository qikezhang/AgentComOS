import os
from unittest import mock
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_config import ExecutorConfig

@mock.patch.dict(os.environ, {
    "CONTROLLED_EXECUTOR_ENABLED": "true",
    "CONTROLLED_EXECUTOR_MODE": "dry_run", 
    "CONTROLLED_EXECUTOR_DEFAULT_DECISION": "deny"
})
def test_non_bypass(tmp_path):
    config = ExecutorConfig()
    fw = ExecutorFramework(config, None)
    req = ExecutorRequest(source="test", command_type="test", command_text_redacted="test")
    req.metadata["adapter_type"] = "shell"
    req.metadata["command_ref"] = "cmd1"
    decision, result = fw.process_request(req, str(tmp_path))
    assert decision.decision == "blocked"
    assert result.status == "blocked"
