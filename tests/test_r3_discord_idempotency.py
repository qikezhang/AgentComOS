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

def test_same_content_different_message_id_creates_separate_commands(base_config, tmp_path):
    message1 = {
        "message_id": "msg_1",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "status"
    }
    message2 = dict(message1, message_id="msg_2")
    
    res1 = ingest_test(message1, tmp_path)
    res2 = ingest_test(message2, tmp_path)
    
    assert res1["status"] == "processed"
    assert res2["status"] == "processed"
    assert res1["gm_command_id"] != res2["gm_command_id"]

def test_duplicate_blocked_arbitrary_command(base_config, tmp_path):
    message = {
        "message_id": "dup_block_1",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "bash -c whoami"
    }
    
    res1 = ingest_test(message, tmp_path)
    assert res1["permission_decision"] == "blocked"
    
    res2 = ingest_test(message, tmp_path)
    assert res2["status"] == "duplicate"
    assert res2["gm_command_id"] == res1["gm_command_id"]

def test_duplicate_secret_request(base_config, tmp_path):
    message = {
        "message_id": "dup_secret_1",
        "guild_id": "g1",
        "channel_id": "c1",
        "author_id_hash": "u1",
        "roles": ["r_ops"],
        "content": "show DISCORD_BOT_TOKEN"
    }
    
    res1 = ingest_test(message, tmp_path)
    assert res1["permission_decision"] == "blocked"
    
    res2 = ingest_test(message, tmp_path)
    assert res2["status"] == "duplicate"
    assert res2["gm_command_id"] == res1["gm_command_id"]
