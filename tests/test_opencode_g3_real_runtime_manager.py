import pytest
from agentcomos.opencode.availability import check_opencode_availability

def test_real_opencode_status_handles_missing_binary(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    status = check_opencode_availability()
    assert status["available"] is False
    assert status["reason"] == "opencode not found"
    assert status["runtime"] == "real_opencode"

def test_real_opencode_status_available(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: "/usr/local/bin/opencode")
    status = check_opencode_availability()
    assert status["available"] is True
    assert status["reason"] == ""
    assert status["runtime"] == "real_opencode"

from agentcomos.opencode.real_runtime import submit_real_job, collect_real_job
from agentcomos.opencode.commands import build_opencode_serve_command, build_opencode_run_attach_command
from agentcomos.opencode.jobs import read_job

def test_real_opencode_submit_requires_existing_run():
    with pytest.raises(ValueError, match="does not exist"):
        submit_real_job("NONEXISTENT-RUN")

def test_real_opencode_submit_missing_binary_creates_blocked_or_unavailable_job(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr("shutil.which", lambda x: None)
    job_id = submit_real_job("OI-TEST-001", "plan")
    
    job = read_job("OI-TEST-001", job_id)
    assert job is not None
    assert job["status"] in ("unavailable", "blocked")
    assert job["real_opencode_used"] is True
    assert job["command"].startswith("opencode run --attach")
    assert "_stderr.log" in job["stderr_log"]

def test_real_opencode_command_builder_uses_expected_serve_command():
    cmd = build_opencode_serve_command("127.0.0.1", 4096)
    assert "opencode serve --hostname 127.0.0.1 --port 4096" in cmd

def test_real_opencode_command_builder_uses_run_attach_when_configured():
    cmd = build_opencode_run_attach_command("RUN-123", "plan")
    assert "opencode run --attach" in cmd
    assert "RUN-123" in cmd

def test_real_collect_missing_job_fails():
    with pytest.raises(ValueError, match="not found"):
        collect_real_job("RUN-123", "NONEXISTENT-JOB")

def test_real_collect_unavailable_job_is_read_only(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    from agentcomos.opencode.jobs import write_job
    write_job("RUN-123", "JOB-123", {"status": "unavailable"})
    
    # Should return without errors
    collect_real_job("RUN-123", "JOB-123")

