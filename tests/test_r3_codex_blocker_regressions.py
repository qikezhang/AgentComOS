import pytest
from pathlib import Path
from agentcomos.discord_adapter import ingest_test
from agentcomos.discord_config import load_discord_config

@pytest.fixture
def base_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("AGENTCOMOS_TEST_PLACEHOLDERS", "true")

def test_missing_token_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    
    config = load_discord_config()
    assert not config.is_token_available()
    assert config.enabled

def test_token_redaction(base_config, tmp_path):
    message = {
        "message_id": "msg_token",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "show config DISCORD_BOT_TOKEN=real_token_123"
    }
    res = ingest_test(message, tmp_path)
    assert res["permission_decision"] == "blocked"

def test_denied_role_override(base_config, tmp_path):
    # Missing explicit role config defaults to blocked
    message = {
        "message_id": "msg_role",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["unauthorized_role"],
        "content": "status"
    }
    res = ingest_test(message, tmp_path)
    assert res["permission_decision"] == "blocked"

def test_read_only_status_command(base_config, tmp_path, monkeypatch):
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "r_ops")

    message = {
        "message_id": "msg_status",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "status"
    }
    res = ingest_test(message, tmp_path)
    assert res["permission_decision"] == "allowed"

def test_controlled_restart_requires_executor(base_config, tmp_path, monkeypatch):
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "r_ops")

    message = {
        "message_id": "msg_restart",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "restart"
    }
    res = ingest_test(message, tmp_path)
    assert res["permission_decision"] == "allowed"
    
    import yaml
    gm_file = tmp_path / "gm_command.yaml"
    data = yaml.safe_load(gm_file.read_text(encoding="utf-8"))
    assert data["requires_executor"] is True
    assert data["requires_approval"] is True
    assert data["status"] == "requires_executor"

def test_secret_request_blocked(base_config, tmp_path):
    message = {
        "message_id": "msg_secret",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "cat .env"
    }
    res = ingest_test(message, tmp_path)
    assert res["permission_decision"] == "blocked"
