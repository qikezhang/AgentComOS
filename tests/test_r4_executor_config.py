import os
from agentcomos.executor_config import ExecutorConfig

def test_missing_config_safe_disabled(monkeypatch):
    monkeypatch.delenv("CONTROLLED_EXECUTOR_ENABLED", raising=False)
    config = ExecutorConfig()
    assert config.is_enabled() is False
    assert config.is_dry_run_only() is True
    assert config.get_default_decision() == "deny"

def test_enabled_false_denies_run(monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    config = ExecutorConfig()
    assert config.is_enabled() is False

def test_dry_run_only_prevents_real_execution(monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_DRY_RUN_ONLY", "true")
    config = ExecutorConfig()
    assert config.is_dry_run_only() is True
