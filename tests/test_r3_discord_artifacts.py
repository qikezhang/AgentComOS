import os
import pytest
from pathlib import Path
import yaml
from agentcomos.discord_adapter import ingest_test

@pytest.fixture
def base_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "r_admin,r_ops")

def test_artifacts_written_and_redacted(base_config, tmp_path):
    message = {
        "message_id": "msg_123",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "status my secret is token=abc"
    }
    
    result = ingest_test(message, tmp_path)
    assert result["status"] == "processed"
    
    # Check Inbound
    inbound_file = tmp_path / "discord_inbound_message.yaml"
    assert inbound_file.exists()
    inbound_data = yaml.safe_load(inbound_file.read_text())
    assert "abc" not in inbound_data["content_redacted"]
    assert "***REDACTED***" in inbound_data["content_redacted"]
    
    # Check Permission Result
    pr_file = tmp_path / "permission_result.yaml"
    assert pr_file.exists()
    
    # Check GM Command
    gmc_file = tmp_path / "gm_command.yaml"
    assert gmc_file.exists()
    gmc_data = yaml.safe_load(gmc_file.read_text())
    assert "abc" not in gmc_data["command_text_redacted"]
    
    # Check Outbound Message
    out_file = tmp_path / "discord_outbound_message.yaml"
    assert out_file.exists()
    
    # Check Audit
    audit_file = tmp_path / "discord_audit.yaml"
    assert audit_file.exists()
    
    # Check Idempotency
    idemp_file = tmp_path / "idempotency" / "msg_123.yaml"
    assert idemp_file.exists()

    # Verify token leak
    for f in tmp_path.glob("**/*.yaml"):
        content = f.read_text()
        assert "real_token_123" not in content
