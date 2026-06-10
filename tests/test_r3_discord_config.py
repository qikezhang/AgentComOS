import os
import pytest
from agentcomos.discord_config import load_discord_config

def test_missing_token_reports_unavailable(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "")
    config = load_discord_config()
    assert config.is_token_available() is False

def test_placeholder_token_reports_unavailable(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "replace-with-deployment-secret")
    config = load_discord_config()
    assert config.is_token_available() is False

def test_token_redacted_in_dump(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "super_secret_token_123")
    config = load_discord_config()
    dump = config.dump_safe()
    assert dump["token"] == "super_secret_token_123=***REDACTED***" or "REDACTED" in dump["token"]
    assert "super_secret_token_123" not in dump["token"]

def test_enabled_false(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "false")
    config = load_discord_config()
    assert config.enabled is False
