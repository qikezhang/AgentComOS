import pytest
from pathlib import Path
import yaml
import shutil
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.loop.plan import create_loop_plan
from agentcomos.loop.runner import run_loop

runner = CliRunner()

@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    run_id = "OI-TECHAI8-LOOP-RECOVER"
    d = Path(".agentcomos/runs") / run_id
    d.mkdir(parents=True, exist_ok=True)
    
    src_intent = Path("examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml")
    shutil.copyfile(src_intent, d / "operating_intent.yaml")
    
    from agentcomos.controller.state import write_run_status
    write_run_status(run_id, {"run_id": run_id, "state": "executing"})
    
    from agentcomos.program.builder import build_operating_program
    from agentcomos.frontier.builder import build_task_frontier
    build_operating_program(run_id)
    build_task_frontier(run_id)
    
    yield d
    shutil.rmtree(d, ignore_errors=True)

def test_loop_trace_requires_run(run_dir: Path):
    res = runner.invoke(app, ["loop", "trace", "--run", "NON_EXISTENT"])
    assert res.exit_code != 0

def test_loop_recover_requires_run(run_dir: Path):
    res = runner.invoke(app, ["loop", "recover", "--run", "NON_EXISTENT"])
    assert res.exit_code != 0

def test_loop_recover_rebuilds_status(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    # Run 2 ticks
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "2", "--fake"])
    
    # Delete status
    (run_dir / "loop_status.yaml").unlink()
    
    # Recover
    res = runner.invoke(app, ["loop", "recover", "--run", run_id])
    assert res.exit_code == 0
    
    # Verify recovered
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["ticks_executed"] == 2
    assert status["tasks_advanced"] == 2
    assert status["status"] == "partial"
