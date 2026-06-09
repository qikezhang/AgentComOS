import pytest
from pathlib import Path
import yaml
from agentcomos.frontier.dependencies import resolve_task_dependencies
from agentcomos.frontier.status import generate_frontier_status
from agentcomos.controller.events import read_events

def setup_frontier(tmp_path: Path, run_id: str, tasks: list[dict]) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)
    frontier = {
        "run_id": run_id,
        "frontier_id": "F-1",
        "tasks": tasks
    }
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier, sort_keys=False))
    
    status = {
        "run_id": run_id,
        "state": "created"
    }
    (run_dir / "run_status.yaml").write_text(yaml.dump(status, sort_keys=False))
    return run_dir

def patch_get_run_dir(tmp_path, monkeypatch):
    def mock_get_run_dir(run_id: str) -> Path:
        return tmp_path / run_id
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.frontier.status.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.frontier.builder.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.artifacts.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.events.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.program.builder.get_run_dir", mock_get_run_dir)

def test_task_awaiting_decision(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "decision_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["awaiting_decision_tasks"]
    assert "TF-001" not in status["ready_tasks"]

def test_task_decision_completed_becomes_ready(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "decision_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    dec_dir = run_dir / "decision" / "TF-001"
    dec_dir.mkdir(parents=True)
    (dec_dir / "decision_result.yaml").write_text(yaml.dump({"status": "completed"}))
    
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["ready_tasks"]
    assert "TF-001" not in status["awaiting_decision_tasks"]

def test_task_awaiting_feynman(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "feynman_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["awaiting_feynman_tasks"]
    assert "TF-001" not in status["ready_tasks"]

def test_task_feynman_completed_passed_becomes_ready(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "feynman_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    feyn_dir = run_dir / "feynman" / "TF-001"
    feyn_dir.mkdir(parents=True)
    (feyn_dir / "feynman_result.yaml").write_text(yaml.dump({"status": "completed", "pass": True}))
    
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["ready_tasks"]
    assert "TF-001" not in status["awaiting_feynman_tasks"]

def test_task_feynman_completed_failed_becomes_blocked(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "feynman_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    feyn_dir = run_dir / "feynman" / "TF-001"
    feyn_dir.mkdir(parents=True)
    (feyn_dir / "feynman_result.yaml").write_text(yaml.dump({"status": "completed", "pass": False}))
    
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["blocked_tasks"]
    
    frontier = yaml.safe_load((run_dir / "task_frontier.yaml").read_text())
    task = frontier["tasks"][0]
    assert task["status"] == "blocked"
    assert task["failure_reason"] == "feynman check failed"

def test_task_both_decision_and_feynman(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_frontier(tmp_path, run_id, [
        {"task_id": "TF-001", "decision_required": True, "feynman_required": True, "depends_on": []}
    ])
    patch_get_run_dir(tmp_path, monkeypatch)
    
    # Missing both -> awaiting_decision first (since decision is checked first)
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["awaiting_decision_tasks"]
    
    # Complete decision -> awaiting_feynman
    dec_dir = run_dir / "decision" / "TF-001"
    dec_dir.mkdir(parents=True)
    (dec_dir / "decision_result.yaml").write_text(yaml.dump({"status": "completed"}))
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["awaiting_feynman_tasks"]
    
    # Complete feynman -> ready
    feyn_dir = run_dir / "feynman" / "TF-001"
    feyn_dir.mkdir(parents=True)
    (feyn_dir / "feynman_result.yaml").write_text(yaml.dump({"status": "completed", "pass": True}))
    status = generate_frontier_status(run_id)
    assert "TF-001" in status["ready_tasks"]
