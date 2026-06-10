import pytest
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.discord_config import load_discord_config

runner = CliRunner()

def test_status_missing_token_unavailable_not_connected(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "token_present: false" in result.stdout
    assert "connected: false" in result.stdout
    assert "token_missing" in result.stdout

def test_status_token_present_does_not_fake_connected_without_connect_check(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_secret_token_777")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "token_present: true" in result.stdout
    assert "connected: false" in result.stdout
    assert "connection_checked: false" in result.stdout
    assert "connect_check_not_requested" in result.stdout

def test_status_redacts_token(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_secret_token_777")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "real_secret_token_777" not in result.stdout

def test_status_connect_check_can_report_connected_only_when_mock_check_succeeds(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_secret_token_777")
    
    async def mock_check():
        return True
    monkeypatch.setattr("agentcomos.discord_runtime.check_discord_connection", mock_check)
    
    result = runner.invoke(app, ["discord", "status", "--connect-check"])
    assert result.exit_code == 0
    assert "token_present: true" in result.stdout
    assert "connected: true" in result.stdout
    assert "connection_checked: true" in result.stdout

def test_status_connect_check_failure_reports_not_connected(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_secret_token_777")
    
    async def mock_check():
        return False
    monkeypatch.setattr("agentcomos.discord_runtime.check_discord_connection", mock_check)
    
    result = runner.invoke(app, ["discord", "status", "--connect-check"])
    assert result.exit_code == 0
    assert "token_present: true" in result.stdout
    assert "connected: false" in result.stdout
    assert "connection_checked: true" in result.stdout
    assert "connect_check_failed" in result.stdout

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
