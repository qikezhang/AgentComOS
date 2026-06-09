import pytest
from pathlib import Path
import yaml
import shutil
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.loop.plan import create_loop_plan
from agentcomos.loop.runner import run_loop
from agentcomos.controller.state import write_run_status
from agentcomos.program.builder import build_operating_program
from agentcomos.frontier.builder import build_task_frontier

runner = CliRunner()

@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    run_id = "OI-TECHAI8-LOOP-RUN"
    d = Path(".agentcomos/runs") / run_id
    d.mkdir(parents=True, exist_ok=True)
    
    # Setup intent to allow frontier build
    src_intent = Path("examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml")
    shutil.copyfile(src_intent, d / "operating_intent.yaml")
    
    # Initial status
    write_run_status(run_id, {"run_id": run_id, "state": "executing"})
    
    # Build program and frontier initially
    build_operating_program(run_id)
    build_task_frontier(run_id)
    
    yield d
    shutil.rmtree(d, ignore_errors=True)

def test_loop_run_requires_max_ticks(run_dir: Path):
    res = runner.invoke(app, ["loop", "run", "--run", run_dir.name, "--fake"])
    assert res.exit_code != 0

def test_loop_run_requires_fake(run_dir: Path):
    create_loop_plan(run_dir.name)
    res = runner.invoke(app, ["loop", "run", "--run", run_dir.name, "--max-ticks", "3"])
    assert res.exit_code != 0

def test_loop_run_rejects_zero_or_negative_max_ticks(run_dir: Path):
    create_loop_plan(run_dir.name)
    res = runner.invoke(app, ["loop", "run", "--run", run_dir.name, "--max-ticks", "0", "--fake"])
    assert res.exit_code != 0

def test_loop_run_advances_three_tasks_with_three_ticks(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["ticks_executed"] <= 3
    assert status["tasks_advanced"] == 3
    assert status["status"] == "partial"

def test_loop_run_writes_trace(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "1", "--fake"])
    trace = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    assert len(trace["ticks"]) == 1
    assert trace["ticks"][0]["tick_number"] == 1

def test_loop_run_writes_status(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "1", "--fake"])
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["ticks_executed"] == 1

def test_loop_run_writes_summary(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "1", "--fake"])
    summary = (run_dir / "loop_summary.md").read_text()
    assert "Ticks executed: 1" in summary

def test_loop_run_stops_on_no_ready_task(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    plan = yaml.safe_load((run_dir / "loop_plan.yaml").read_text())
    plan["max_task_advancements"] = 10
    (run_dir / "loop_plan.yaml").write_text(yaml.dump(plan))
    
    # Run more ticks than tasks
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "10", "--fake"])
    assert res.exit_code == 0
    
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "no_ready_task"

def test_loop_run_stops_on_failed_task(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "failed"
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "failed_task"

def test_loop_run_stops_on_awaiting_decision(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "blocked"
    frontier["tasks"][0]["decision_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "awaiting_decision"

def test_loop_run_stops_on_awaiting_feynman(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "blocked"
    frontier["tasks"][0]["feynman_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "awaiting_feynman"
