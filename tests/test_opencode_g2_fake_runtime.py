import pytest
import yaml
from pathlib import Path
from agentcomos.opencode.fake_runtime import submit_fake_job, collect_fake_job, status_fake_job
from agentcomos.opencode.jobs import get_job_path, get_opencode_logs_dir, get_opencode_outputs_dir
from agentcomos.controller.state import get_run_dir

def test_fake_opencode_submit_generates_job(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-1"
    
    job_id = submit_fake_job(run_id)
    assert job_id == f"OCJ-{run_id}-001"
    
    job_path = get_job_path(run_id, job_id)
    assert job_path.exists()
    job_data = yaml.safe_load(job_path.read_text())
    assert job_data["status"] == "completed"
    assert job_data["fake_runtime"] is True
    assert job_data["real_opencode_used"] is False

def test_fake_opencode_submit_generates_plan(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-2"
    
    submit_fake_job(run_id)
    
    outputs_dir = get_opencode_outputs_dir(run_id)
    plan_path = outputs_dir / "opencode_project_plan.yaml"
    assert plan_path.exists()
    plan_data = yaml.safe_load(plan_path.read_text())
    assert plan_data["produced_by"] == "fake_opencode"

def test_fake_opencode_submit_generates_logs(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-3"
    
    job_id = submit_fake_job(run_id)
    
    logs_dir = get_opencode_logs_dir(run_id)
    assert (logs_dir / f"{job_id}.stdout.log").exists()
    assert (logs_dir / f"{job_id}.stderr.log").exists()

def test_fake_opencode_submit_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-4"
    
    job_id1 = submit_fake_job(run_id)
    # Write some garbage to plan to see if it gets overwritten (it shouldn't)
    plan_path = get_opencode_outputs_dir(run_id) / "opencode_project_plan.yaml"
    plan_path.write_text("custom data")
    
    job_id2 = submit_fake_job(run_id)
    assert job_id1 == job_id2
    assert plan_path.read_text() == "custom data"

def test_fake_opencode_collect_reads_completed_job(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-5"
    job_id = submit_fake_job(run_id)
    
    # Should pass without exceptions
    collect_fake_job(run_id, job_id)

def test_opencode_collect_missing_job_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    with pytest.raises(ValueError, match="not found"):
        collect_fake_job("test", "OCJ-test-001")

def test_fake_opencode_status_reads_job(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    run_id = "test-run-6"
    job_id = submit_fake_job(run_id)
    
    status_fake_job(run_id, job_id)
    captured = capsys.readouterr()
    assert "fake_opencode" in captured.out

def test_opencode_status_missing_job_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    with pytest.raises(ValueError, match="not found"):
        status_fake_job("test", "OCJ-test-001")
