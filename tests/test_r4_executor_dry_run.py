import os
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_request import ExecutorRequest

def test_dry_run_result_written(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    config = ExecutorConfig()
    framework = ExecutorFramework(config) # no policy => blocks
    
    req = ExecutorRequest("discord", "unknown", "do something")
    dec, res = framework.process_request(req, str(tmp_path))
    
    assert res.status == "blocked"
    assert res.execution_mode == "dry_run"
    assert res.real_execution is False
    assert res.adapter_invoked is False
    assert os.path.exists(tmp_path / f"executor_result_{res.executor_result_id}.yaml")
