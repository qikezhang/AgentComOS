import pytest
from pathlib import Path
from agentcomos.discord_adapter import ingest_test

@pytest.fixture
def base_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")

def test_duplicate_message(base_config, tmp_path):
    message = {
        "message_id": "dup_123",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "status"
    }
    
    res1 = ingest_test(message, tmp_path)
    assert res1["status"] == "processed"
    
    res2 = ingest_test(message, tmp_path)
    assert res2["status"] == "duplicate"
    assert res2["gm_command_id"] == res1["gm_command_id"]
