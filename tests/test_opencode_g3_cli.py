import pytest
from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def test_opencode_start_command():
    result = runner.invoke(app, ["opencode", "start"])
    assert result.exit_code == 0
    assert "opencode serve" in result.stdout

def test_opencode_status_availability(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    result = runner.invoke(app, ["opencode", "status"])
    assert result.exit_code == 0
    assert "opencode not found" in result.stdout

def test_opencode_submit_requires_fake_or_real():
    result = runner.invoke(app, ["opencode", "submit", "--run", "OI-TEST-001"])
    assert result.exit_code != 0
    assert "Must specify either --fake or --real" in str(result.output) or "Must specify either --fake or --real" in str(result.exception)

def test_unavailable_real_job_routes_to_real_status_even_when_real_opencode_used_false(monkeypatch, tmp_path):
    from agentcomos.opencode.jobs import write_job
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    # create real unavailable job
    job_data = {
        "job_id": "OCJ-TEST-001",
        "run_id": "TEST",
        "runtime": "real_opencode",
        "real_opencode_used": False,
        "attempted_real_opencode": True,
        "status": "unavailable"
    }
    write_job("TEST", "OCJ-TEST-001", job_data)
    
    result = runner.invoke(app, ["opencode", "status", "--job", "OCJ-TEST-001"])
    assert result.exit_code == 0
    assert "real_opencode" in result.stdout
    assert "unavailable" in result.stdout

def test_unavailable_real_job_routes_to_real_collect_even_when_real_opencode_used_false(monkeypatch, tmp_path):
    from agentcomos.opencode.jobs import write_job
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    job_data = {
        "job_id": "OCJ-TEST-001",
        "run_id": "TEST",
        "runtime": "real_opencode",
        "real_opencode_used": False,
        "attempted_real_opencode": True,
        "status": "unavailable"
    }
    write_job("TEST", "OCJ-TEST-001", job_data)
    
    result = runner.invoke(app, ["opencode", "collect", "--job", "OCJ-TEST-001"])
    assert result.exit_code == 0
    assert "Real job collected or in read-only mode" in result.stdout

def test_runtime_field_has_priority_over_real_opencode_used():
    from agentcomos.opencode.jobs import detect_job_runtime
    job = {
        "runtime": "real_opencode",
        "real_opencode_used": False,
        "attempted_real_opencode": True
    }
    assert detect_job_runtime(job) == "real"
    
    job2 = {
        "runtime": "fake_opencode",
        "real_opencode_used": True  # contradictory, but runtime wins
    }
    assert detect_job_runtime(job2) == "fake"

def test_fake_job_still_routes_to_fake_path(monkeypatch, tmp_path):
    from agentcomos.opencode.jobs import write_job
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    job_data = {
        "job_id": "OCJ-TEST-001",
        "run_id": "TEST",
        "runtime": "fake_opencode",
        "real_opencode_used": False,
        "fake_runtime": True,
        "status": "completed"
    }
    write_job("TEST", "OCJ-TEST-001", job_data)
    
    result = runner.invoke(app, ["opencode", "status", "--job", "OCJ-TEST-001"])
    assert result.exit_code == 0
    assert "fake_opencode" in result.stdout

def test_unknown_job_runtime_fails_safely(monkeypatch, tmp_path):
    from agentcomos.opencode.jobs import write_job
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    job_data = {
        "job_id": "OCJ-TEST-001",
        "run_id": "TEST",
        "status": "completed"
    }
    write_job("TEST", "OCJ-TEST-001", job_data)
    
    result = runner.invoke(app, ["opencode", "status", "--job", "OCJ-TEST-001"])
    assert result.exit_code != 0
    assert "Cannot determine runtime type" in str(result.output) or "Cannot determine runtime type" in str(result.exception)
