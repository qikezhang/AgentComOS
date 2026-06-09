import pytest
import yaml
from pathlib import Path
from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

def mock_get_run_dir(tmp_path: Path):
    def _mock(run_id: str) -> Path:
        return tmp_path / run_id
    return _mock

def setup_reporting_env(tmp_path, monkeypatch, run_id):
    mock = mock_get_run_dir(tmp_path)
    import agentcomos.controller.state as state
    import agentcomos.controller.events as ev
    import agentcomos.evidence.builder as ev_builder
    import agentcomos.delivery.builder as dl_builder
    import agentcomos.gm.report as gm_report
    import agentcomos.evidence.artifact_index as ai
    
    monkeypatch.setattr(state, "get_run_dir", mock)
    monkeypatch.setattr(ev, "get_run_dir", mock)
    monkeypatch.setattr(ev_builder.state, "get_run_dir", mock)
    monkeypatch.setattr(dl_builder.state, "get_run_dir", mock)
    monkeypatch.setattr(gm_report.state, "get_run_dir", mock)
    monkeypatch.setattr(ai.state, "get_run_dir", mock)
    
    run_dir = mock(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # create required basic files
    with open(run_dir / "events.jsonl", "w") as f:
        f.write('{"type": "run.created", "timestamp": "2026-06-09T00:00:00Z", "payload": {}}\n')
    with open(run_dir / "timeline.yaml", "w") as f:
        yaml.dump({"events": []}, f)
    with open(run_dir / "task_frontier.yaml", "w") as f:
        yaml.dump({"run_id": run_id, "tasks": [{"task_id": "TF-001", "status": "awaiting_manual_os", "manual_os_required": True}]}, f)
    with open(run_dir / "frontier_status.yaml", "w") as f:
        yaml.dump({"awaiting_manual_os_tasks": ["TF-001"]}, f)
    
    (run_dir / "manual_os" / "TF-001").mkdir(parents=True, exist_ok=True)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_request.yaml", "w") as f:
        yaml.dump({"status": "requested"}, f)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_approval.yaml", "w") as f:
        yaml.dump({"status": "approved"}, f)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_audit.md", "w") as f:
        f.write("# Audit")
        
    return run_dir

def test_evidence_indexes_manual_os_request(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    res = runner.invoke(app, ["evidence", "build", "--run", run_id])
    assert res.exit_code == 0
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data = yaml.safe_load(f)
        paths = [a["path"] for a in data["artifacts"]]
        assert "manual_os/TF-001/manual_os_request.yaml" in paths

def test_evidence_indexes_manual_os_approval(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data = yaml.safe_load(f)
        paths = [a["path"] for a in data["artifacts"]]
        assert "manual_os/TF-001/manual_os_approval.yaml" in paths

def test_evidence_indexes_manual_os_result(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_result.yaml", "w") as f:
        yaml.dump({"status": "completed"}, f)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data = yaml.safe_load(f)
        paths = [a["path"] for a in data["artifacts"]]
        assert "manual_os/TF-001/manual_os_result.yaml" in paths

def test_evidence_indexes_manual_os_audit(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data = yaml.safe_load(f)
        paths = [a["path"] for a in data["artifacts"]]
        assert "manual_os/TF-001/manual_os_audit.md" in paths

def test_evidence_manual_os_artifact_index_is_stable(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data1 = f.read()
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data2 = f.read()
    
    assert data1 == data2

def test_evidence_reports_missing_manual_os_result_for_blocked_task(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    with open(run_dir / "evidence_packet" / "artifact_index.yaml") as f:
        data = yaml.safe_load(f)
        entry = next((a for a in data["artifacts"] if a["path"] == "manual_os/TF-001/manual_os_result.yaml"), None)
        assert entry is not None
        assert entry["exists"] is False

def test_delivery_includes_manual_os_request(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    res = runner.invoke(app, ["delivery", "build", "--run", run_id])
    assert res.exit_code == 0
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert "manual_os/TF-001/manual_os_request.yaml" in data["artifacts"]

def test_delivery_includes_manual_os_approval(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert "manual_os/TF-001/manual_os_approval.yaml" in data["artifacts"]

def test_delivery_includes_manual_os_result(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_result.yaml", "w") as f:
        yaml.dump({"status": "completed"}, f)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert "manual_os/TF-001/manual_os_result.yaml" in data["artifacts"]

def test_delivery_includes_manual_os_audit(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert "manual_os/TF-001/manual_os_audit.md" in data["artifacts"]

def test_delivery_not_completed_when_awaiting_manual_os(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert data["status"] in ("partial", "blocked", "needs_manual_os", "failed")
        assert data["status"] != "completed"

def test_delivery_discloses_manual_os_next_action(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert any("human approval/result required" in a for a in data["next_actions"])

def test_delivery_completed_after_manual_os_result_completed(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    with open(run_dir / "manual_os" / "TF-001" / "manual_os_result.yaml", "w") as f:
        yaml.dump({"status": "completed"}, f)
    # Remove awaiting_manual_os status
    with open(run_dir / "frontier_status.yaml", "w") as f:
        yaml.dump({"awaiting_manual_os_tasks": []}, f)
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    with open(run_dir / "delivery_packet.yaml") as f:
        data = yaml.safe_load(f)
        assert data["status"] != "partial"

def test_gm_report_discloses_manual_os_controlled_adoption(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["controlled_adoption_enabled"] is True

def test_gm_report_discloses_auto_execute_false(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["auto_execute"] is False

def test_gm_report_discloses_human_approval_required(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["human_approval_required"] is True

def test_gm_report_discloses_human_result_report_required(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["human_result_report_required"] is True

def test_gm_report_discloses_agent_did_not_execute_shell(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["agent_executed_shell"] is False

def test_gm_report_discloses_agent_did_not_execute_ssh(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["agent_executed_ssh"] is False

def test_gm_report_discloses_agent_did_not_execute_sudo(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["agent_executed_sudo"] is False

def test_gm_report_discloses_agent_did_not_execute_docker_systemctl(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["agent_executed_docker"] is False
        assert data["manual_os"]["agent_executed_systemctl"] is False

def test_gm_report_discloses_next_action_when_awaiting_manual_os(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert "human must approve or reject" in data["manual_os"]["next_action"]

def test_gm_report_does_not_imply_autonomous_os_operation(tmp_path, monkeypatch):
    run_id = "OI-TEST"
    run_dir = setup_reporting_env(tmp_path, monkeypatch, run_id)
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    with open(run_dir / "gm_report.yaml") as f:
        data = yaml.safe_load(f)
        assert data["manual_os"]["autonomous_os_operation"] is False
