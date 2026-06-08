import pytest
import yaml
from pathlib import Path
from agentcomos.delivery.builder import build_delivery_packet, get_delivery_status

def test_delivery_build_generates_delivery_packet(tmp_path, monkeypatch):
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
    
    build_delivery_packet("RUN-1")
    assert (run_dir / "delivery_packet.yaml").exists()

def test_delivery_references_evidence_and_gm_report(tmp_path, monkeypatch):
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
    
    build_delivery_packet("RUN-1")
    data = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert "evidence_packet/manifest.yaml" in data["artifacts"]
    assert "gm_report.md" in data["artifacts"]

def test_delivery_missing_evidence_is_not_completed(tmp_path, monkeypatch):
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
    
    build_delivery_packet("RUN-1")
    data = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert data["status"] != "completed"

def test_repeated_delivery_build_is_idempotent(tmp_path, monkeypatch):
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
    
    build_delivery_packet("RUN-1")
    data1 = (run_dir / "delivery_packet.yaml").read_text()
    
    build_delivery_packet("RUN-1")
    data2 = (run_dir / "delivery_packet.yaml").read_text()
    
    assert data1 == data2
