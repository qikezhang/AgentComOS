import pytest
import yaml
from pathlib import Path
from agentcomos.gm.report import generate_gm_report

def test_gm_report_generates_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    generate_gm_report("RUN-1", format="markdown")
    assert (run_dir / "gm_report.md").exists()

def test_gm_report_generates_yaml(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    generate_gm_report("RUN-1", format="yaml")
    assert (run_dir / "gm_report.yaml").exists()

def test_gm_report_discloses_fake_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    (run_dir / "evidence_packet").mkdir()
    (run_dir / "evidence_packet" / "runtime_summary.yaml").write_text(yaml.dump({
        "opencode": {"fake_opencode_used": True, "real_opencode_attempted": False, "real_opencode_used": False},
        "hermes": {"fake_hermes_used": True, "real_hermes_attempted": False, "real_hermes_used": False},
        "worker": {"tmux_used": False}
    }))
    
    generate_gm_report("RUN-1", format="markdown")
    text = (run_dir / "gm_report.md").read_text()
    assert "Fake OpenCode: True" in text
    assert "Fake Hermes: True" in text

def test_gm_report_discloses_unavailable_real_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    (run_dir / "evidence_packet").mkdir()
    (run_dir / "evidence_packet" / "runtime_summary.yaml").write_text(yaml.dump({
        "opencode": {"fake_opencode_used": False, "real_opencode_attempted": True, "real_opencode_used": False},
        "hermes": {"fake_hermes_used": False, "real_hermes_attempted": True, "real_hermes_used": False},
        "worker": {"tmux_used": False}
    }))
    
    generate_gm_report("RUN-1", format="yaml")
    data = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert data["runtime_usage"]["real_opencode_attempted"] is True
    assert data["runtime_usage"]["real_opencode_used"] is False

def test_gm_report_does_not_claim_missing_artifacts_exist(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    generate_gm_report("RUN-1", format="yaml")
    data = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert data["status"] != "completed"

def test_repeated_gm_report_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcomos.controller.state.get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id)
    import agentcomos.controller.events
    monkeypatch.setattr(agentcomos.controller.events, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.builder
    monkeypatch.setattr(agentcomos.evidence.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.summaries
    monkeypatch.setattr(agentcomos.evidence.summaries, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.artifact_index
    monkeypatch.setattr(agentcomos.evidence.artifact_index, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.evidence.validation
    monkeypatch.setattr(agentcomos.evidence.validation, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.delivery.builder
    monkeypatch.setattr(agentcomos.delivery.builder, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    import agentcomos.gm.report
    monkeypatch.setattr(agentcomos.gm.report, "get_run_dir", lambda run_id: tmp_path / ".agentcomos" / "runs" / run_id, raising=False)
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-1"
    run_dir.mkdir(parents=True)
    
    generate_gm_report("RUN-1", format="markdown")
    text1 = (run_dir / "gm_report.md").read_text()
    
    generate_gm_report("RUN-1", format="markdown")
    text2 = (run_dir / "gm_report.md").read_text()
    
    assert text1 == text2
    
def test_g6_timeline_is_updated():
    pass
