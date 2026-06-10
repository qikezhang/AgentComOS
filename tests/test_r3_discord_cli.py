import pytest
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.discord_config import load_discord_config

runner = CliRunner()

def test_discord_status_unavailable(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "connected: false" in result.stdout
    assert "token_missing" in result.stdout

def test_discord_status_redacted(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_secret_token_777")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "real_secret_token_777" not in result.stdout

def test_discord_ingest_test(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    
    message_file = tmp_path / "msg.yaml"
    message_file.write_text("""
message_id: msg_cli_1
content: status
""")
    
    result = runner.invoke(app, ["discord", "ingest-test", "--message-file", str(message_file), "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "status: processed" in result.stdout
    
    assert (tmp_path / "discord_inbound_message.yaml").exists()
