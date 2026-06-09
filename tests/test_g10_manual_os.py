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

def setup_run_env(tmp_path, monkeypatch, run_id, task_id=None):
    mock = mock_get_run_dir(tmp_path)
    import agentcomos.manual_os.request as req
    import agentcomos.manual_os.status as st
    import agentcomos.manual_os.approval as app_os
    import agentcomos.manual_os.result as res_os
    import agentcomos.manual_os.audit as aud_os
    import agentcomos.controller.state as state
    import agentcomos.controller.events as ev
    
    monkeypatch.setattr(req, "get_run_dir", mock)
    monkeypatch.setattr(st, "get_run_dir", mock)
    monkeypatch.setattr(app_os, "get_run_dir", mock)
    monkeypatch.setattr(res_os, "get_run_dir", mock)
    monkeypatch.setattr(aud_os, "get_run_dir", mock)
    monkeypatch.setattr(state, "get_run_dir", mock)
    monkeypatch.setattr(ev, "get_run_dir", mock)
    
    monkeypatch.chdir(tmp_path)
    
    run_dir = mock(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    if task_id:
        with open(run_dir / "task_frontier.yaml", "w") as f:
            yaml.dump({"tasks": [{"task_id": task_id}]}, f)
    return run_dir

def test_manual_os_request_generates_artifact(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
        
    res = runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    assert res.exit_code == 0
    
    request_file = run_dir / "manual_os" / task_id / "manual_os_request.yaml"
    assert request_file.exists()
    
    with open(request_file, "r") as f:
        data = yaml.safe_load(f)
        assert data["status"] == "requested"
        assert data["safety"]["auto_execute"] is False
        assert data["safety"]["requires_human_approval"] is True

def test_manual_os_request_requires_existing_run():
    res = runner.invoke(app, ["manual-os", "request", "--run", "NON_EXISTENT", "--task", "TF-001"])
    assert res.exit_code != 0

def test_manual_os_request_requires_existing_task(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    setup_run_env(tmp_path, monkeypatch, run_id, "TF-OTHER")
        
    res = runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", "TF-001"])
    assert res.exit_code != 0

def test_manual_os_request_is_idempotent(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
        
    res1 = runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    assert res1.exit_code == 0
    
    request_file = run_dir / "manual_os" / task_id / "manual_os_request.yaml"
    mtime1 = request_file.stat().st_mtime
    
    res2 = runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    assert res2.exit_code == 0
    
    mtime2 = request_file.stat().st_mtime
    assert mtime1 == mtime2
    
    events_file = run_dir / "events.jsonl"
    with open(events_file, "r") as f:
        events = [json.loads(line) for line in f if line.strip()]
        
    requested_events = [e for e in events if e["type"] == "manual_os.requested"]
    assert len(requested_events) == 1

def test_manual_os_status_is_read_only(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
        
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    
    events_file = run_dir / "events.jsonl"
    mtime1 = events_file.stat().st_mtime
    
    res = runner.invoke(app, ["manual-os", "status", "--run", run_id])
    assert res.exit_code == 0
    assert task_id in res.stdout
    
    mtime2 = events_file.stat().st_mtime
    assert mtime1 == mtime2

def test_manual_os_approve_requires_request(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    res = runner.invoke(app, ["manual-os", "approve", "--run", run_id, "--task", task_id, "--approved-by", "operator"])
    assert res.exit_code != 0
    assert "does not exist" in res.stdout or res.exception

def test_manual_os_approve_requires_approved_by(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    
    res = runner.invoke(app, ["manual-os", "approve", "--run", run_id, "--task", task_id])
    assert res.exit_code != 0

def test_manual_os_reject_requires_request(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    res = runner.invoke(app, ["manual-os", "reject", "--run", run_id, "--task", task_id, "--rejected-by", "operator", "--reason", "no"])
    assert res.exit_code != 0

def test_manual_os_reject_requires_reason(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    
    res = runner.invoke(app, ["manual-os", "reject", "--run", run_id, "--task", task_id, "--rejected-by", "operator"])
    assert res.exit_code != 0

def test_manual_os_result_requires_request(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    res = runner.invoke(app, ["manual-os", "result", "--run", run_id, "--task", task_id, "--status", "completed", "--executed-by", "operator", "--summary", "done"])
    assert res.exit_code != 0

def test_manual_os_result_completed_requires_approval(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    
    res = runner.invoke(app, ["manual-os", "result", "--run", run_id, "--task", task_id, "--status", "completed", "--executed-by", "operator", "--summary", "done"])
    assert res.exit_code != 0

def test_manual_os_result_records_completed(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    res1 = runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    assert res1.exit_code == 0, res1.exception
    res2 = runner.invoke(app, ["manual-os", "approve", "--run", run_id, "--task", task_id, "--approved-by", "operator"])
    assert res2.exit_code == 0, res2.exception
    res = runner.invoke(app, ["manual-os", "result", "--run", run_id, "--task", task_id, "--status", "completed", "--executed-by", "operator", "--summary", "done"])
    assert res.exit_code == 0, res.exception
    
    res_file = run_dir / "manual_os" / task_id / "manual_os_result.yaml"
    assert res_file.exists()
    with open(res_file, "r") as f:
        data = yaml.safe_load(f)
        assert data["status"] == "completed"

def test_manual_os_result_records_failed(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    # Failed does not strictly require approval, or does it? It shouldn't if they failed setup.
    res = runner.invoke(app, ["manual-os", "result", "--run", run_id, "--task", task_id, "--status", "failed", "--executed-by", "operator", "--summary", "failed"])
    assert res.exit_code == 0
    
    res_file = run_dir / "manual_os" / task_id / "manual_os_result.yaml"
    assert res_file.exists()
    with open(res_file, "r") as f:
        data = yaml.safe_load(f)
        assert data["status"] == "failed"

def test_manual_os_audit_generates_markdown(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    runner.invoke(app, ["manual-os", "approve", "--run", run_id, "--task", task_id, "--approved-by", "operator"])
    runner.invoke(app, ["manual-os", "result", "--run", run_id, "--task", task_id, "--status", "completed", "--executed-by", "operator", "--summary", "done"])
    
    res = runner.invoke(app, ["manual-os", "audit", "--run", run_id])
    assert res.exit_code == 0
    
    audit_file = run_dir / "manual_os" / task_id / "manual_os_audit.md"
    assert audit_file.exists()
    with open(audit_file, "r") as f:
        content = f.read()
        assert "Manual OS Audit" in content

def test_manual_os_audit_is_idempotent(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    run_dir = setup_run_env(tmp_path, monkeypatch, run_id, task_id)
    
    runner.invoke(app, ["manual-os", "request", "--run", run_id, "--task", task_id])
    runner.invoke(app, ["manual-os", "audit", "--run", run_id])
    
    audit_file = run_dir / "manual_os" / task_id / "manual_os_audit.md"
    mtime1 = audit_file.stat().st_mtime
    
    runner.invoke(app, ["manual-os", "audit", "--run", run_id])
    mtime2 = audit_file.stat().st_mtime
    
    assert mtime1 == mtime2

def test_loop_blocks_on_manual_os(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    task_id = "TF-001"
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / ".agentcomos" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock get_run_dir so other parts that use it point here too
    import agentcomos.controller.state as state
    monkeypatch.setattr(state, "get_run_dir", lambda r: run_dir)
    import agentcomos.controller.events as ev
    monkeypatch.setattr(ev, "get_run_dir", lambda r: run_dir)
    
    with open(run_dir / "task_frontier.yaml", "w") as f:
        yaml.dump({"tasks": [{"task_id": task_id, "status": "ready", "manual_os_required": True}]}, f)
        
    with open(run_dir / "loop_plan.yaml", "w") as f:
        yaml.dump({"max_task_advancements": 5}, f)
        
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--fake", "--max-ticks", "1"])
    assert res.exit_code == 0, res.exception
    
    status_file = run_dir / "loop_status.yaml"
    with open(status_file, "r") as f:
        status = yaml.safe_load(f)
        assert status["status"] == "blocked"
        assert status["stop_reason"] == "awaiting_manual_os"
        
    trace_file = run_dir / "loop_trace.yaml"
    with open(trace_file, "r") as f:
        trace = yaml.safe_load(f)
        assert len(trace["ticks"]) == 1
        assert trace["ticks"][0]["result"] == "blocked"
        assert trace["ticks"][0]["stop_reason"] == "awaiting_manual_os"
