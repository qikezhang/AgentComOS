from typer.testing import CliRunner
from agentcomos.cli import app
import os

runner = CliRunner()

def test_executor_status_cli():
    result = runner.invoke(app, ["executor", "status"])
    assert result.exit_code == 0
    assert "enabled:" in result.stdout
    assert "real_execution_available: false" in result.stdout
    assert "adapters_available: false" in result.stdout

def test_executor_evaluate_cli(tmp_path):
    result = runner.invoke(app, ["executor", "evaluate", "--request-file", "tests/fixtures/executor/read_only_status_request.yaml", "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "executor_request_id:" in result.stdout

def test_executor_run_dry_cli(tmp_path):
    result = runner.invoke(app, ["executor", "run-dry", "--request-file", "tests/fixtures/executor/read_only_status_request.yaml", "--runtime-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "executor_request_id:" in result.stdout
    assert "execution_mode: dry_run" in result.stdout
