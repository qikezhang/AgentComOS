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
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["decision_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "awaiting_decision"
    assert status["status"] == "blocked"

def test_loop_run_stops_on_awaiting_feynman(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["feynman_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status["stop_reason"] == "awaiting_feynman"
    assert status["status"] == "blocked"

def test_repeated_terminal_loop_run_does_not_append_no_ready_tick(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    plan = yaml.safe_load((run_dir / "loop_plan.yaml").read_text())
    plan["max_task_advancements"] = 10
    (run_dir / "loop_plan.yaml").write_text(yaml.dump(plan))
    
    # First run reaches end of tasks
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "5", "--fake"])
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    ticks1 = status["ticks_executed"]
    assert status["status"] == "completed"
    
    # Second run should do nothing
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "5", "--fake"])
    status2 = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    assert status2["ticks_executed"] == ticks1

def test_loop_trace_records_awaiting_decision_block(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["decision_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    trace = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    assert len(trace["ticks"]) >= 1
    tick = trace["ticks"][0]
    assert tick["result"] == "blocked"
    assert tick["blocked_on"]["type"] == "decision"
    assert tick["blocked_on"]["reason"] == "awaiting_decision"
    assert tick["advanced_task_id"] is None
    assert tick["controller_tick_called"] is False
    assert tick["real_runtime_used"] is False
    
    decision_dir = run_dir / "decision"
    if decision_dir.exists():
        results = list(decision_dir.glob("**/decision_result.yaml"))
        assert len(results) == 0

def test_loop_trace_records_awaiting_feynman_block(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["feynman_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    assert res.exit_code == 0
    trace = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    assert len(trace["ticks"]) >= 1
    tick = trace["ticks"][0]
    assert tick["result"] == "blocked"
    assert tick["blocked_on"]["type"] == "feynman"
    assert tick["blocked_on"]["reason"] == "awaiting_feynman"
    assert tick["advanced_task_id"] is None
    assert tick["controller_tick_called"] is False
    assert tick["real_runtime_used"] is False
    
    feynman_dir = run_dir / "feynman"
    if feynman_dir.exists():
        results = list(feynman_dir.glob("**/feynman_result.yaml"))
        assert len(results) == 0

def test_blocked_tick_trace_is_counted_once(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["decision_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    trace1 = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    ticks_len = len(trace1["ticks"])
    assert ticks_len >= 1
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    trace2 = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    assert len(trace2["ticks"]) == ticks_len

def test_blocked_tick_trace_matches_status_stop_reason(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["decision_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    status = yaml.safe_load((run_dir / "loop_status.yaml").read_text())
    trace = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    last_tick = trace["ticks"][-1]
    
    assert status["stop_reason"] == last_tick["stop_reason"]
    assert status["blocked_on"]["type"] == last_tick["blocked_on"]["type"]
    assert status["blocked_on"]["task_id"] == last_tick["blocked_on"]["task_id"]

def test_blocked_tick_trace_does_not_call_controller_tick(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    frontier["tasks"][0]["status"] = "ready"
    frontier["tasks"][0]["feynman_required"] = True
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "3", "--fake"])
    
    # task should not be completed
    updated_frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    assert updated_frontier["tasks"][0]["status"] != "completed"
    
    trace = yaml.safe_load((run_dir / "loop_trace.yaml").read_text())
    last_tick = trace["ticks"][-1]
    assert last_tick["controller_tick_called"] is False
