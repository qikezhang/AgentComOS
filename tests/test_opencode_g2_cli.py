import pytest
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.controller.runner import handle_run_create
from agentcomos.controller.state import RunState, write_run_status
from agentcomos.opencode.fake_runtime import submit_fake_job

runner = CliRunner()

def patch_get_run_dir(monkeypatch, tmp_path):
    def fake_get_run_dir(run_id):
        return tmp_path / "runs" / run_id
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", fake_get_run_dir)
    monkeypatch.setattr("agentcomos.controller.runner.get_run_dir", fake_get_run_dir, raising=False)
    monkeypatch.setattr("agentcomos.controller.artifacts.get_run_dir", fake_get_run_dir, raising=False)
    monkeypatch.setattr("agentcomos.opencode.jobs.get_run_dir", fake_get_run_dir, raising=False)

def test_cli_opencode_submit_fake(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    run_id = "cli-test-submit"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    
    result = runner.invoke(app, ["opencode", "submit", "--run", run_id, "--fake"])
    assert result.exit_code == 0
    assert "Fake job submitted" in result.stdout

def test_cli_opencode_submit_real_fails(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    run_id = "cli-test-submit"
    
    result = runner.invoke(app, ["opencode", "submit", "--run", run_id], env={"TERMINAL_WIDTH": "10000", "COLUMNS": "10000"})
    assert result.exit_code != 0
    assert "either --fake or --real" in result.output

def test_cli_opencode_status(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    run_id = "cli-test-status"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    job_id = submit_fake_job(run_id)
    
    result = runner.invoke(app, ["opencode", "status", "--job", job_id])
    assert result.exit_code == 0
    assert "fake_opencode" in result.stdout

def test_cli_opencode_collect(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    run_id = "cli-test-collect"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: accepted\n", encoding="utf-8")
    (run_dir / "delivery_packet.yaml").write_text("artifacts: []\n", encoding="utf-8")
    job_id = submit_fake_job(run_id)
    
    result = runner.invoke(app, ["opencode", "collect", "--job", job_id])
    assert result.exit_code == 0

def test_controller_tick_fake_does_not_duplicate_opencode_job(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    
    intent_file = tmp_path / "intent.yaml"
    intent_file.write_text("run_id: cli-test-tick")
    handle_run_create(intent_file)
    
    run_id = "cli-test-tick"
    
    # Tick to planning
    runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"]) # -> accepted
    runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"]) # -> context_ready
    runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"]) # -> planning
    
    from agentcomos.opencode.jobs import get_opencode_jobs_dir
    jobs_dir = get_opencode_jobs_dir(run_id)
    jobs = list(jobs_dir.glob("*.yaml"))
    assert len(jobs) == 1
    
    # Tick to executing
    runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"]) # -> executing
    jobs = list(jobs_dir.glob("*.yaml"))
    assert len(jobs) == 1 # still 1

def test_g2_delivery_packet_includes_opencode_outputs(tmp_path, monkeypatch):
    patch_get_run_dir(monkeypatch, tmp_path)
    run_id = "cli-test-delivery"
    intent_file = tmp_path / "intent.yaml"
    intent_file.write_text(f"run_id: {run_id}")
    handle_run_create(intent_file)
    
    # Run through all states to generate delivery packet
    for _ in range(8):
        runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"])
        
    delivery_path = tmp_path / "runs" / run_id / "delivery_packet.yaml"
    assert delivery_path.exists()
    
    import yaml
    packet = yaml.safe_load(delivery_path.read_text())
    assert "fake_opencode" in packet["produced_by"]
    artifacts = packet["artifacts"]
    assert any("opencode_jobs/" in a for a in artifacts)
    assert any("opencode_outputs/" in a for a in artifacts)
