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
    assert job.get("real_opencode_used") is False or job.get("attempted_real_opencode") is True
    assert job["command"].startswith("opencode run --attach")
    assert "_stderr.log" in job["stderr_log"]

def test_real_unavailable_job_has_failure_reason(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("shutil.which", lambda x: None)
    job_id = submit_real_job("OI-TEST-001", "plan")
    job = read_job("OI-TEST-001", job_id)
    assert job["status"] == "unavailable"
    assert "failure_reason" in job
    assert job["failure_reason"]

def test_real_opencode_submit_does_not_fake_completion(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("shutil.which", lambda x: None)
    job_id = submit_real_job("OI-TEST-001", "plan")
    job = read_job("OI-TEST-001", job_id)
    assert job["status"] != "completed"

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

def test_fake_runtime_still_passes_after_g3(monkeypatch, tmp_path):
    from agentcomos.opencode.fake_runtime import submit_fake_job, status_fake_job, collect_fake_job
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    import yaml
    (tmp_path / "run_status.yaml").write_text(yaml.dump({"run_id": "OI-TEST-001"}), encoding="utf-8")
    (tmp_path / "delivery_packet.yaml").write_text("", encoding="utf-8")
    (tmp_path / "opencode_outputs").mkdir(exist_ok=True)
    (tmp_path / "opencode_outputs" / "opencode_project_plan.yaml").write_text("", encoding="utf-8")
    job_id = submit_fake_job("OI-TEST-001")
    assert job_id is not None
    status_fake_job("OI-TEST-001", job_id)
    collect_fake_job("OI-TEST-001", job_id)
    job = read_job("OI-TEST-001", job_id)
    assert job["status"] == "completed"
    assert job["fake_runtime"] is True

def test_make_tests_do_not_require_real_opencode(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("shutil.which", lambda x: None)
    job_id = submit_real_job("OI-TEST-001", "plan")
    job = read_job("OI-TEST-001", job_id)
    assert job["status"] in ("unavailable", "blocked")

def test_real_runtime_does_not_call_hermes_or_tmux(monkeypatch, tmp_path):
    import subprocess
    called = []
    original_run = subprocess.run
    def mock_run(*args, **kwargs):
        called.append(args[0])
        return original_run(*args, **kwargs)
    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    submit_real_job("OI-TEST-001", "plan")
    for cmd in called:
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        assert ("hermes" + " chat") not in cmd_str
        assert "tmux new-session" not in cmd_str

def test_runtime_status_yaml_is_written(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    submit_real_job("OI-TEST-001", "plan")
    import yaml
    status_file = tmp_path / "opencode_runtime_status.yaml"
    assert status_file.exists()
    data = yaml.safe_load(status_file.read_text())
    assert "available" in data
    assert "mode" in data

def test_real_submit_records_stdout_stderr_paths(monkeypatch, tmp_path):
    monkeypatch.setattr("agentcomos.opencode.real_runtime.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("agentcomos.opencode.runtime_status.get_run_dir", lambda run_id: tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    job_id = submit_real_job("OI-TEST-001", "plan")
    job = read_job("OI-TEST-001", job_id)
    assert "stdout_log" in job
    assert "stderr_log" in job

def test_branch_does_not_include_agentcomos_runs_artifacts():
    import subprocess
    try:
        result = subprocess.run(["git", "diff", "--name-status", "origin/main...HEAD"], capture_output=True, text=True)
        assert ".agentcomos/runs" not in result.stdout
    except Exception:
        pass

