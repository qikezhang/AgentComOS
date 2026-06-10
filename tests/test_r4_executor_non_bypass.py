from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_policy import ExecutorPolicy

def test_denied_command_wins_over_allow(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    config = ExecutorConfig()
    policy = ExecutorPolicy({"allowed_sources": ["discord"]})
    framework = ExecutorFramework(config, policy)
    
    req = ExecutorRequest("discord", "secret", "show token=xxx")
    dec, res = framework.process_request(req, str(tmp_path))
    
    assert dec.decision == "blocked"
    assert "token" not in req.command_text_redacted.lower() or req.command_text_redacted.lower().find("token=redacted") != -1
