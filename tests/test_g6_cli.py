from typer.testing import CliRunner
from agentcomos.cli import app
import pytest

runner = CliRunner()

def test_evidence_build_missing_run():
    result = runner.invoke(app, ["evidence", "build", "--run", "RUN-MISSING"])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_evidence_status_missing_run():
    result = runner.invoke(app, ["evidence", "status", "--run", "RUN-MISSING"])
    assert result.exit_code == 0
    assert "missing_run" in result.output

def test_delivery_build_missing_run():
    result = runner.invoke(app, ["delivery", "build", "--run", "RUN-MISSING"])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_delivery_status_missing_run():
    result = runner.invoke(app, ["delivery", "status", "--run", "RUN-MISSING"])
    assert result.exit_code == 0
    assert "missing_run" in result.output

def test_gm_report_missing_run():
    result = runner.invoke(app, ["gm", "report", "--run", "RUN-MISSING"])
    assert result.exit_code != 0
    assert "does not exist" in result.output
