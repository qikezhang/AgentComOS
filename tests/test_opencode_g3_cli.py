import pytest
from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def test_opencode_start_command():
    result = runner.invoke(app, ["opencode", "start"])
    assert result.exit_code == 0
    assert "opencode serve" in result.stdout

def test_opencode_status_availability(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    result = runner.invoke(app, ["opencode", "status"])
    assert result.exit_code == 0
    assert "opencode not found" in result.stdout

def test_opencode_submit_requires_fake_or_real():
    result = runner.invoke(app, ["opencode", "submit", "--run", "OI-TEST-001"])
    assert result.exit_code != 0
    assert "Must specify either --fake or --real" in str(result.output) or "Must specify either --fake or --real" in str(result.exception)
