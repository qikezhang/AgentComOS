from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def test_adapter_status():
    result = runner.invoke(app, ["adapter", "status"])
    assert result.exit_code == 0
    assert "shell" in result.stdout
