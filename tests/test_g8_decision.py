import pytest
from pathlib import Path
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.controller.events import read_events
from agentcomos.decision.status import get_decision_status, get_decision_result

runner = CliRunner()

def setup_mock_run(tmp_path: Path, run_id: str) -> Path:
    import yaml
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)
    frontier = {
        "tasks": [
            {"task_id": "TF-001"}
        ]
    }
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier, sort_keys=False))
    return run_dir

def patch_get_run_dir(tmp_path, monkeypatch, module="decision"):
    def mock_get_run_dir(run_id: str) -> Path:
        return tmp_path / run_id
    monkeypatch.setattr(f"agentcomos.{module}.builder.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr(f"agentcomos.{module}.status.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.frontier.builder.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.artifacts.get_run_dir", mock_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.events.get_run_dir", mock_get_run_dir)

def test_decision_request_generates_artifacts(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    
    result = runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    assert result.exit_code == 0
    assert (run_dir / "decision" / "TF-001" / "decision_request.yaml").exists()
    assert (run_dir / "decision" / "TF-001" / "decision_result.yaml").exists()

def test_decision_requires_explicit_mode(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    
    result = runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "wrong"])
    assert result.exit_code != 0
    assert "mode must be 'explicit'" in result.output

def test_decision_rejects_missing_mode(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    
    result = runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001"])
    assert result.exit_code != 0

def test_decision_missing_run_fails(tmp_path, monkeypatch):
    patch_get_run_dir(tmp_path, monkeypatch)
    result = runner.invoke(app, ["decision", "request", "--run", "missing", "--task", "TF-001", "--mode", "explicit"])
    assert result.exit_code != 0
    assert "Run missing not found" in result.output

def test_decision_missing_task_fails(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    
    result = runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-002", "--mode", "explicit"])
    assert result.exit_code != 0
    assert "Task TF-002 not found" in result.output

def test_decision_status_is_read_only(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    
    events_before = len(read_events(run_id))
    result = runner.invoke(app, ["decision", "status", "--run", run_id])
    assert result.exit_code == 0
    events_after = len(read_events(run_id))
    assert events_before == events_after

def test_decision_result_is_read_only(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    
    events_before = len(read_events(run_id))
    result = runner.invoke(app, ["decision", "result", "--run", run_id, "--task", "TF-001"])
    assert result.exit_code == 0
    events_after = len(read_events(run_id))
    assert events_before == events_after

def test_decision_events_are_appended(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    
    events = read_events(run_id)
    types = [e["type"] for e in events]
    assert "decision.requested" in types
    assert "decision.completed" in types

def test_decision_timeline_is_updated(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    
    import yaml
    timeline = yaml.safe_load((run_dir / "timeline.yaml").read_text())
    types = [e["type"] for e in timeline.get("events", [])]
    assert "decision.requested" in types
    assert "decision.completed" in types

def test_decision_does_not_call_real_runtime(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    
    import yaml
    res = yaml.safe_load((run_dir / "decision" / "TF-001" / "decision_result.yaml").read_text())
    assert res.get("real_runtime_used") is False

def test_decision_request_is_idempotent(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    events_before = len(read_events(run_id))
    
    runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "explicit"])
    events_after = len(read_events(run_id))
    assert events_before == events_after

def test_decision_invalid_mode_fails(tmp_path, monkeypatch):
    run_id = "R-1"
    run_dir = setup_mock_run(tmp_path, run_id)
    patch_get_run_dir(tmp_path, monkeypatch)
    result = runner.invoke(app, ["decision", "request", "--run", run_id, "--task", "TF-001", "--mode", "invalid"])
    assert result.exit_code != 0

def test_missing_run_does_not_create_orphan_decision(tmp_path, monkeypatch):
    patch_get_run_dir(tmp_path, monkeypatch)
    runner.invoke(app, ["decision", "request", "--run", "missing", "--task", "TF-001", "--mode", "explicit"])
    assert not (tmp_path / "missing").exists()
