import pytest
import yaml
from pathlib import Path
from agentcomos.opencode.fake_runtime import submit_fake_job, collect_fake_job, status_fake_job
from agentcomos.opencode.jobs import get_job_path, get_opencode_logs_dir, get_opencode_outputs_dir
from agentcomos.controller.state import get_run_dir

def setup_valid_run(tmp_path, run_id):
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    (run_dir / "delivery_packet.yaml").write_text("artifacts: []\n", encoding="utf-8")
    return run_dir

def test_fake_opencode_submit_generates_job(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-1"
    setup_valid_run(tmp_path, run_id)
    
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
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-2"
    setup_valid_run(tmp_path, run_id)
    
    submit_fake_job(run_id)
    
    outputs_dir = get_opencode_outputs_dir(run_id)
    plan_path = outputs_dir / "opencode_project_plan.yaml"
    assert plan_path.exists()
    plan_data = yaml.safe_load(plan_path.read_text())
    assert plan_data["produced_by"] == "fake_opencode"

def test_fake_opencode_submit_generates_logs(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-3"
    setup_valid_run(tmp_path, run_id)
    
    job_id = submit_fake_job(run_id)
    
    logs_dir = get_opencode_logs_dir(run_id)
    assert (logs_dir / f"{job_id}.stdout.log").exists()
    assert (logs_dir / f"{job_id}.stderr.log").exists()

def test_fake_opencode_submit_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-4"
    setup_valid_run(tmp_path, run_id)
    
    job_id1 = submit_fake_job(run_id)
    # Write some garbage to plan to see if it gets overwritten (it shouldn't)
    plan_path = get_opencode_outputs_dir(run_id) / "opencode_project_plan.yaml"
    plan_path.write_text("custom data")
    
    job_id2 = submit_fake_job(run_id)
    assert job_id1 == job_id2
    assert plan_path.read_text() == "custom data"

def test_fake_opencode_collect_reads_completed_job(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-5"
    setup_valid_run(tmp_path, run_id)
    job_id = submit_fake_job(run_id)
    
    # Should pass without exceptions
    collect_fake_job(run_id, job_id)

def test_opencode_collect_missing_job_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    with pytest.raises(ValueError, match="not found"):
        collect_fake_job("test", "OCJ-test-001")

def test_fake_opencode_status_reads_job(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-6"
    setup_valid_run(tmp_path, run_id)
    job_id = submit_fake_job(run_id)
    
    status_fake_job(run_id, job_id)
    captured = capsys.readouterr()
    assert "fake_opencode" in captured.out

def test_opencode_status_missing_job_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    with pytest.raises(ValueError, match="not found"):
        status_fake_job("test", "OCJ-test-001")

def test_opencode_submit_missing_run_fails_without_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "OI-DOES-NOT-EXIST"
    
    with pytest.raises(ValueError, match="does not exist"):
        submit_fake_job(run_id)
        
    run_dir = tmp_path / "runs" / run_id
    assert not (run_dir / "opencode_jobs").exists()
    assert not (run_dir / "opencode_logs").exists()
    assert not (run_dir / "opencode_outputs").exists()

def test_opencode_submit_missing_run_status_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "OI-BROKEN"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    
    with pytest.raises(ValueError, match="does not exist"):
        submit_fake_job(run_id)
        
    assert not (run_dir / "opencode_jobs").exists()

def test_opencode_collect_missing_delivery_packet_fails_read_only(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "OI-COLLECT-TEST"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(yaml.dump({"run_id": run_id}))
    
    # Fake submit works
    job_id = submit_fake_job(run_id)
    
    # Now simulate collect but without delivery packet
    delivery_packet = run_dir / "delivery_packet.yaml"
    if delivery_packet.exists():
        delivery_packet.unlink()
    
    job_path = get_job_path(run_id, job_id)
    mtime_before = job_path.stat().st_mtime
    
    with pytest.raises(ValueError, match="delivery_packet.yaml is missing"):
        collect_fake_job(run_id, job_id)
        
    assert job_path.stat().st_mtime == mtime_before

def test_fake_opencode_submit_generates_delivery_packet(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-dp"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    
    submit_fake_job(run_id)
    
    dp_path = run_dir / "delivery_packet.yaml"
    assert dp_path.exists()
    dp_data = yaml.safe_load(dp_path.read_text())
    assert dp_data["status"] == "completed"
    assert "opencode_outputs/opencode_project_plan.yaml" in dp_data["artifacts"]

def test_fake_opencode_collect_succeeds_after_submit_delivery_exists(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-collect-succ"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    
    job_id = submit_fake_job(run_id)
    collect_fake_job(run_id, job_id)  # Should not raise

def test_fake_submit_appends_delivery_updated_event(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-events"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    
    submit_fake_job(run_id)
    
    events_path = run_dir / "events.jsonl"
    events_text = events_path.read_text()
    assert "delivery.updated" in events_text

def test_fake_submit_updates_timeline_with_delivery_updated(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.controller.artifacts
    monkeypatch.setattr(agentcomos.controller.artifacts, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.jobs
    monkeypatch.setattr(agentcomos.opencode.jobs, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    import agentcomos.opencode.fake_runtime
    monkeypatch.setattr(agentcomos.opencode.fake_runtime, "get_run_dir", lambda run_id: tmp_path / "runs" / run_id, raising=False)
    run_id = "test-run-timeline"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    
    submit_fake_job(run_id)
    
    timeline_path = run_dir / "timeline.yaml"
    assert timeline_path.exists()
    timeline_data = yaml.safe_load(timeline_path.read_text())
    
    types = [e["type"] for e in timeline_data["events"]]
    assert "delivery.updated" in types
