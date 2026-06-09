import os
import json
import yaml
from pathlib import Path

from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def mock_get_run_dir(tmp_path: Path):
    def _mock(run_id: str) -> Path:
        return tmp_path / run_id
    return _mock

def setup_run_env(tmp_path, monkeypatch, run_id, task_id="TF-001"):
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / ".agentcomos" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "task_frontier.yaml", "w") as f:
        yaml.dump({"run_id": run_id, "tasks": [{"task_id": task_id, "status": "awaiting_manual_os", "manual_os_required": True}]}, f)
        
    with open(run_dir / "loop_plan.yaml", "w") as f:
        yaml.dump({"max_task_advancements": 5}, f)
        
    return run_dir

def test_loop_stops_on_awaiting_manual_os(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "3"])
    assert res.exit_code == 0, res.exception
    
    with open(run_dir / "loop_status.yaml") as f:
        status = yaml.safe_load(f)
        assert status["status"] == "blocked"
        assert status["stop_reason"] == "awaiting_manual_os"

def test_loop_status_records_awaiting_manual_os(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    with open(run_dir / "loop_status.yaml") as f:
        status = yaml.safe_load(f)
        assert status["blocked_on"]["type"] == "manual_os"
        assert status["blocked_on"]["task_id"] == "TF-001"

def test_loop_trace_records_manual_os_blocked_tick(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    with open(run_dir / "loop_trace.yaml") as f:
        trace = yaml.safe_load(f)
        tick = trace["ticks"][0]
        assert tick["result"] == "blocked"
        assert tick["blocked_on"]["type"] == "manual_os"

def test_loop_manual_os_block_controller_tick_called_false(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    with open(run_dir / "loop_trace.yaml") as f:
        trace = yaml.safe_load(f)
        tick = trace["ticks"][0]
        assert tick["controller_tick_called"] is False

def test_loop_does_not_auto_create_manual_os_approval(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    assert not (run_dir / "manual_os" / "TF-001" / "manual_os_approval.yaml").exists()

def test_loop_does_not_auto_create_manual_os_result(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    assert not (run_dir / "manual_os" / "TF-001" / "manual_os_result.yaml").exists()

def test_manual_os_block_is_not_reported_as_no_ready_task(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    with open(run_dir / "loop_status.yaml") as f:
        status = yaml.safe_load(f)
        assert status["stop_reason"] != "no_ready_task"
        assert status["status"] != "completed"

def test_manual_os_block_is_not_reported_as_completed(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    
    with open(run_dir / "loop_status.yaml") as f:
        status = yaml.safe_load(f)
        assert status["status"] != "completed"

def test_completed_manual_os_result_unblocks_task(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id)
    
    (run_dir / "manual_os" / "TF-001").mkdir(parents=True, exist_ok=True)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_result.yaml", "w") as f:
        yaml.dump({"status": "completed"}, f)
        
    with open(run_dir / "task_frontier.yaml", "w") as f:
        yaml.dump({"run_id": run_id, "tasks": [{"task_id": "TF-001", "status": "ready", "manual_os_required": True}]}, f)
        
    import agentcomos.loop.runner as loop_runner
    monkeypatch.setattr(loop_runner, "handle_controller_tick", lambda r, fake: {"status": "advanced", "task_id": "TF-001"})
    
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    assert res.exit_code == 0, res.exception
    
    with open(run_dir / "loop_status.yaml") as f:
        status = yaml.safe_load(f)
        assert status["stop_reason"] != "awaiting_manual_os"
        
