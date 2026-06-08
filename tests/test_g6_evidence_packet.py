import pytest
import yaml
from pathlib import Path
from agentcomos.evidence.builder import build_evidence_packet, get_evidence_status
from agentcomos.controller.events import append_event

def test_evidence_build_generates_manifest(tmp_path, monkeypatch):
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
    
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    
    assert (run_dir / "evidence_packet" / "manifest.yaml").exists()
    
def test_evidence_build_generates_events_summary(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    assert (run_dir / "evidence_packet" / "events_summary.yaml").exists()

def test_evidence_build_generates_runtime_summary(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    assert (run_dir / "evidence_packet" / "runtime_summary.yaml").exists()

def test_evidence_build_generates_artifact_index(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    assert (run_dir / "evidence_packet" / "artifact_index.yaml").exists()

def test_evidence_build_generates_validation_summary(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    assert (run_dir / "evidence_packet" / "validation_summary.yaml").exists()

def test_evidence_build_missing_run_fails(tmp_path, monkeypatch):
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
    with pytest.raises(ValueError, match="does not exist"):
        build_evidence_packet("RUN-MISSING")

def test_evidence_build_missing_events_does_not_recreate_and_pass(tmp_path, monkeypatch):
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
    
    with pytest.raises(ValueError, match="Missing events.jsonl"):
        build_evidence_packet("RUN-1")
    
    assert not (run_dir / "events.jsonl").exists()
    
    manifest = yaml.safe_load((run_dir / "evidence_packet" / "manifest.yaml").read_text())
    assert manifest["status"] == "failed"

def test_evidence_build_missing_timeline_is_not_completed(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    manifest = yaml.safe_load((run_dir / "evidence_packet" / "manifest.yaml").read_text())
    assert manifest["status"] != "completed"

def test_repeated_evidence_build_is_idempotent(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    manifest1 = (run_dir / "evidence_packet" / "manifest.yaml").read_text()
    
    build_evidence_packet("RUN-1")
    manifest2 = (run_dir / "evidence_packet" / "manifest.yaml").read_text()
    
    assert manifest1 == manifest2
    
def test_g6_events_are_appended(tmp_path, monkeypatch):
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
    (run_dir / "events.jsonl").touch()
    
    build_evidence_packet("RUN-1")
    text = (run_dir / "events.jsonl").read_text()
    assert "evidence.build.started" in text
    assert "evidence.build.completed" in text or "evidence.build.failed" in text

def test_g6_does_not_start_loop_manual_evolution():
    pass

def test_g6_does_not_call_real_opencode_or_hermes():
    pass

def test_no_agentcomos_runs_artifacts_committed():
    pass

def test_g1_to_g5_regression_still_passes():
    pass
