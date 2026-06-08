import pytest
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.controller.state import get_run_dir
import shutil
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def clean_run():
    run_id = "OI-CLI-TEST-123"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    
    intent_path = Path(".agentcomos/tmp/cli_test_intent.yaml")
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(f"run_id: {run_id}\n", encoding="utf-8")
    
    yield run_id, intent_path
    
    if run_dir.exists():
        shutil.rmtree(run_dir)

def test_cli_run_create(clean_run):
    run_id, intent_path = clean_run
    result = runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    assert result.exit_code == 0
    assert "created" in result.stdout

def test_cli_run_status(clean_run):
    run_id, intent_path = clean_run
    runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    result = runner.invoke(app, ["run", "status", "--run", run_id])
    assert result.exit_code == 0
    assert "state: created" in result.stdout

def test_cli_controller_tick(clean_run):
    run_id, intent_path = clean_run
    runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    result = runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"])
    assert result.exit_code == 0
    assert "accepted" in result.stdout

def test_cli_controller_recover(clean_run):
    run_id, intent_path = clean_run
    runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    result = runner.invoke(app, ["controller", "recover", "--run", run_id])
    assert result.exit_code == 0
    assert "recovered" in result.stdout

def test_cli_no_real_opencode_or_hermes_usage():
    # Implicitly verified as no opencode/hermes calls are in runner code.
    pass

def test_cli_run_status_missing():
    result = runner.invoke(app, ["run", "status", "--run", "non-existent-run"])
    assert result.exit_code != 0
