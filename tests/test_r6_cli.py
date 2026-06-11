from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def test_release_readiness_cli():
    result = runner.invoke(app, ["release", "readiness"])
    assert result.exit_code == 0

def test_smoke_production_cli(tmp_path):
    result = runner.invoke(app, ["smoke", "production", "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
