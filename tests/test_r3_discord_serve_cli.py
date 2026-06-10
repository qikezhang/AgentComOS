import pytest
from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def test_discord_serve_cli_exists():
    result = runner.invoke(app, ["discord", "serve", "--help"])
    assert result.exit_code == 0
    assert "Serve the real Discord bot runtime." in result.output

def test_serve_missing_token_unavailable_no_connect(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    
    result = runner.invoke(app, ["discord", "serve", "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Discord adapter unavailable: token_missing" in result.output

def test_serve_disabled_returns_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "false")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "fake_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    result = runner.invoke(app, ["discord", "serve", "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Discord adapter unavailable: disabled" in result.output

def test_serve_output_redacts_token(monkeypatch, tmp_path):
    # Not easily testable at CLI level since serve does not print token anyway,
    # but we can check status instead for redaction.
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "real_token_123" not in result.output
    assert "token_present: true" in result.output

def test_status_token_present_does_not_fake_connected(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    result = runner.invoke(app, ["discord", "status"])
    assert result.exit_code == 0
    assert "connected: false" in result.output
    assert "reason: connect_check_not_requested" in result.output

def test_status_connect_check_failure_reports_not_connected(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    import agentcomos.discord_runtime
    async def fake_check():
        return False
    monkeypatch.setattr(agentcomos.discord_runtime, "check_discord_connection", fake_check)

    result = runner.invoke(app, ["discord", "status", "--connect-check"])
    assert result.exit_code == 0
    assert "connected: false" in result.output
    assert "reason: connect_check_failed" in result.output

def test_status_connect_check_can_report_connected_only_when_mock_check_succeeds(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    import agentcomos.discord_runtime
    async def fake_check():
        return True
    monkeypatch.setattr(agentcomos.discord_runtime, "check_discord_connection", fake_check)

    result = runner.invoke(app, ["discord", "status", "--connect-check"])
    assert result.exit_code == 0
    assert "connected: true" in result.output
    assert "connection_checked: true" in result.output
