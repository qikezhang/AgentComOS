import os
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_request import ExecutorRequest

def test_executor_artifacts_written(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    config = ExecutorConfig()
    framework = ExecutorFramework(config)
    
    req = ExecutorRequest("discord", "status", "status")
    dec, res = framework.process_request(req, str(tmp_path))
    
    assert os.path.exists(tmp_path / f"executor_request_{req.executor_request_id}.yaml")
    assert os.path.exists(tmp_path / f"executor_decision_{dec.decision_id}.yaml")
    assert os.path.exists(tmp_path / f"executor_result_{res.executor_result_id}.yaml")
    assert os.path.exists(tmp_path / "executor_audit.yaml")


