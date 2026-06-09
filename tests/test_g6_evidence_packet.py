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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
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
    (run_dir / "timeline.yaml").touch()
    
    build_evidence_packet("RUN-1")
    text = (run_dir / "events.jsonl").read_text()
    assert "evidence.build.started" in text
    assert "evidence.build.completed" in text or "evidence.build.failed" in text

def test_g6_does_not_start_loop_manual_evolution():
    src_dir = Path("src/agentcomos/evidence")
    delivery_dir = Path("src/agentcomos/delivery")
    gm_dir = Path("src/agentcomos/gm")
    
    for dir_path in [src_dir, delivery_dir, gm_dir]:
        for f in dir_path.rglob("*.py"):
            lines = f.read_text(encoding="utf-8").lower().splitlines()
            for line in lines:
                if "worker evolution" in line or "auto versioner" in line:
                    assert "not enabled" in line or "disabled" in line

def test_g6_does_not_call_real_opencode_or_hermes():
    src_dir = Path("src/agentcomos/evidence")
    delivery_dir = Path("src/agentcomos/delivery")
    gm_dir = Path("src/agentcomos/gm")
    
    for dir_path in [src_dir, delivery_dir, gm_dir]:
        for f in dir_path.rglob("*.py"):
            text = f.read_text(encoding="utf-8")
            assert "opencode serve" not in text
            assert "opencode run" not in text
            assert "run --attach" not in text
            assert "hermes chat" not in text
            assert "tmux new-session" not in text
            assert "tmux send-keys" not in text
            assert "discord" not in text.lower()

def test_no_agentcomos_runs_artifacts_committed():
    import subprocess
    result = subprocess.run(["git", "diff", "--name-status", "origin/main...HEAD"], capture_output=True, text=True)
    if result.returncode == 0:
        assert ".agentcomos/runs" not in result.stdout
        assert "uv.lock" not in result.stdout
    else:
        # fallback if origin/main doesn't exist
        result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
        assert ".agentcomos/runs" not in result.stdout
        assert "uv.lock" not in result.stdout

def test_g1_to_g5_regression_still_passes():
    from typer.testing import CliRunner
    from agentcomos.cli import app
    runner = CliRunner()
    
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "run" in res.stdout
    assert "controller" in res.stdout
    assert "opencode" in res.stdout
    assert "worker" in res.stdout
    assert "evidence" in res.stdout
    assert "delivery" in res.stdout
    assert "gm" in res.stdout

def test_g1_to_g5_minimal_fake_flow_still_works(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    from typer.testing import CliRunner
    from agentcomos.cli import app
    
    runner = CliRunner()
    
    intent_path = tmp_path / "intent.yaml"
    intent_content = """
intent_id: "OI-TEST-001"
created_by: "gm"
source: "discord"
goal: "test"
success_criteria: []
constraints: []
risk_level: "medium"
"""
    intent_path.write_text(intent_content)
    
    res = runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    assert res.exit_code == 0
    
    runs_dir = tmp_path / ".agentcomos" / "runs"
    runs = list(runs_dir.glob("*"))
    assert len(runs) == 1
    run_id = runs[0].name
    
    res = runner.invoke(app, ["opencode", "submit", "--run", run_id, "--fake"])
    assert res.exit_code == 0
    
    res = runner.invoke(app, ["opencode", "collect", "--job", f"OCJ-{run_id}-001"])
    assert res.exit_code == 0
    
    res = runner.invoke(app, ["evidence", "build", "--run", run_id])
    assert res.exit_code == 0

def test_g6_timeline_includes_evidence_delivery_gm_events(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from agentcomos.evidence.builder import build_evidence_packet
    from agentcomos.gm.report import generate_gm_report
    from agentcomos.delivery.builder import build_delivery_packet
    import agentcomos.controller.state as state
    import yaml
    
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-TL"
    run_dir.mkdir(parents=True)
    (run_dir / "timeline.yaml").touch()
    (run_dir / "events.jsonl").write_text('{"event_id": "1", "timestamp": "1", "type": "run.created", "run_id": "RUN-TL"}\n')
    
    build_evidence_packet("RUN-TL")
    generate_gm_report("RUN-TL", format="yaml")
    build_delivery_packet("RUN-TL")
    
    tl_path = run_dir / "timeline.yaml"
    assert tl_path.exists()
    
    data = yaml.safe_load(tl_path.read_text())
    types = [e["type"] for e in data.get("events", [])]
    
    assert "evidence.build.completed" in types
    assert "gm.report.completed" in types
    assert "delivery.updated" in types
    assert "delivery.build.completed" in types

def test_g6_timeline_is_stable_on_repeated_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from agentcomos.evidence.builder import build_evidence_packet
    import agentcomos.controller.state as state
    
    run_dir = tmp_path / ".agentcomos" / "runs" / "RUN-TL-STABLE"
    run_dir.mkdir(parents=True)
    (run_dir / "timeline.yaml").touch()
    (run_dir / "events.jsonl").write_text('{"event_id": "1", "timestamp": "1", "type": "run.created", "run_id": "RUN-TL-STABLE"}\n')
    
    build_evidence_packet("RUN-TL-STABLE")
    tl_path = run_dir / "timeline.yaml"
    hash1 = tl_path.read_text()
    
    build_evidence_packet("RUN-TL-STABLE")
    hash2 = tl_path.read_text()
    
    assert hash1 == hash2

