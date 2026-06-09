import pytest
import yaml
import shutil
import json
from pathlib import Path

from agentcomos.evidence.artifact_index import generate_artifact_index
from agentcomos.delivery.builder import build_delivery_packet
from agentcomos.gm.report import generate_gm_report
from agentcomos.controller.state import get_run_dir

@pytest.fixture
def fake_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_id = "TEST-G8-RUN"
    run_dir = tmp_path / ".agentcomos" / "runs" / run_id
    run_dir.mkdir(parents=True)
    
    # write fake frontier
    frontier = {
        "frontier_id": "TF-TEST",
        "status": "active",
        "tasks": [
            {"task_id": "T1", "decision_required": True, "status": "blocked"},
            {"task_id": "T2", "feynman_required": True, "status": "blocked"}
        ]
    }
    (run_dir / "task_frontier.yaml").write_text(yaml.dump(frontier))
    
    # write minimal files to avoid evidence builder crash
    (run_dir / "events.jsonl").write_text('{"type": "init", "timestamp": "2026-06-09T00:00:00Z"}\n')
    (run_dir / "timeline.yaml").write_text("[]\n")
    (run_dir / "evidence_packet").mkdir()
    (run_dir / "evidence_packet" / "manifest.yaml").write_text("status: completed\n")
    (run_dir / "evidence_packet" / "runtime_summary.yaml").write_text("{}\n")
    
    return run_id, run_dir

def test_g8_evidence_indexes_decision_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_request.yaml").write_text("type: req\n")
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    
    generate_artifact_index(run_id)
    
    index = yaml.safe_load((run_dir / "evidence_packet" / "artifact_index.yaml").read_text())
    artifacts = {a["path"]: a for a in index["artifacts"]}
    assert "decision/T1/decision_request.yaml" in artifacts
    assert artifacts["decision/T1/decision_request.yaml"]["exists"] is True
    assert artifacts["decision/T1/decision_request.yaml"]["phase"] == "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION"
    assert artifacts["decision/T1/decision_result.yaml"]["exists"] is True

def test_g8_evidence_indexes_feynman_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_check.yaml").write_text("type: chk\n")
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    
    generate_artifact_index(run_id)
    
    index = yaml.safe_load((run_dir / "evidence_packet" / "artifact_index.yaml").read_text())
    artifacts = {a["path"]: a for a in index["artifacts"]}
    assert "feynman/T2/feynman_check.yaml" in artifacts
    assert artifacts["feynman/T2/feynman_check.yaml"]["exists"] is True
    assert artifacts["feynman/T2/feynman_result.yaml"]["exists"] is True

def test_g8_evidence_marks_missing_required_decision_result(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_request.yaml").write_text("type: req\n")
    generate_artifact_index(run_id)
    index = yaml.safe_load((run_dir / "evidence_packet" / "artifact_index.yaml").read_text())
    artifacts = {a["path"]: a for a in index["artifacts"]}
    assert artifacts["decision/T1/decision_result.yaml"]["exists"] is False

def test_g8_evidence_marks_missing_required_feynman_result(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_check.yaml").write_text("type: chk\n")
    generate_artifact_index(run_id)
    index = yaml.safe_load((run_dir / "evidence_packet" / "artifact_index.yaml").read_text())
    artifacts = {a["path"]: a for a in index["artifacts"]}
    assert artifacts["feynman/T2/feynman_result.yaml"]["exists"] is False

def test_g8_artifact_index_is_stable(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_request.yaml").write_text("req")
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("res")
    
    generate_artifact_index(run_id)
    txt1 = (run_dir / "evidence_packet" / "artifact_index.yaml").read_text()
    generate_artifact_index(run_id)
    txt2 = (run_dir / "evidence_packet" / "artifact_index.yaml").read_text()
    assert txt1 == txt2

def test_g8_delivery_includes_decision_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_request.yaml").write_text("type: req\n")
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert "decision/T1/decision_request.yaml" in packet["artifacts"]
    assert "decision/T1/decision_result.yaml" in packet["artifacts"]
    assert len(packet["g8_controls"]["decision"]) > 0

def test_g8_delivery_includes_feynman_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_check.yaml").write_text("type: chk\n")
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert "feynman/T2/feynman_check.yaml" in packet["artifacts"]

def test_g8_delivery_not_completed_when_awaiting_decision(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "frontier_status.yaml").write_text(yaml.dump({"awaiting_decision_tasks": ["T1"]}))
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert packet["status"] == "partial"

def test_g8_delivery_not_completed_when_awaiting_feynman(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "frontier_status.yaml").write_text(yaml.dump({"awaiting_feynman_tasks": ["T2"]}))
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert packet["status"] == "partial"

def test_g8_delivery_not_completed_when_required_decision_missing(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_request.yaml").write_text("type: req\n")
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert packet["status"] in ("failed", "partial")

def test_g8_delivery_not_completed_when_required_feynman_missing(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_check.yaml").write_text("type: chk\n")
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert packet["status"] in ("failed", "partial")

def test_g8_delivery_completed_when_required_results_exist(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    # need evidence completed
    (run_dir / "evidence_packet" / "artifact_index.yaml").write_text("{}")
    (run_dir / "evidence_packet" / "validation_summary.yaml").write_text("{}")
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    
    assert packet.get("status") == "completed"
    
    delivery_text = (run_dir / "delivery_packet.yaml").read_text()
    assert "decision/T1/decision_result.yaml" in delivery_text
    assert "feynman/T2/feynman_result.yaml" in delivery_text
    assert "awaiting_decision" not in delivery_text
    assert "awaiting_feynman" not in delivery_text
    
    g8 = packet.get("g8_controls", {})
    assert g8
    assert "decision" in g8
    assert "feynman" in g8

def test_g8_delivery_discloses_g8_blocking_issues(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "frontier_status.yaml").write_text(yaml.dump({"awaiting_decision_tasks": ["T1"]}))
    build_delivery_packet(run_id)
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert any("awaiting_decision" in r for r in packet["risks"])

def test_g8_gm_report_discloses_explicit_decision(fake_run):
    run_id, run_dir = fake_run
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["g8_controls"]["decision_controlled_mode"] == "explicit"

def test_g8_gm_report_discloses_explicit_feynman(fake_run):
    run_id, run_dir = fake_run
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["g8_controls"]["feynman_controlled_mode"] == "explicit"

def test_g8_gm_report_discloses_no_automatic_decision_market(fake_run):
    run_id, run_dir = fake_run
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["g8_controls"]["automatic_decision_market_enabled"] is False

def test_g8_gm_report_discloses_no_automatic_feynman_executor(fake_run):
    run_id, run_dir = fake_run
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["g8_controls"]["automatic_feynman_executor_enabled"] is False

def test_g8_gm_report_discloses_real_runtime_false(fake_run):
    run_id, run_dir = fake_run
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["g8_controls"]["real_runtime_used"] is False

def test_g8_gm_report_not_completed_when_awaiting_decision(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "frontier_status.yaml").write_text(yaml.dump({"awaiting_decision_tasks": ["T1"]}))
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["status"] in ("failed", "partial")

def test_g8_gm_report_not_completed_when_awaiting_feynman(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "frontier_status.yaml").write_text(yaml.dump({"awaiting_feynman_tasks": ["T2"]}))
    generate_gm_report(run_id, format="yaml")
    r = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert r["status"] in ("failed", "partial")

def test_g8_gm_report_lists_decision_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    generate_gm_report(run_id, format="markdown")
    md = (run_dir / "gm_report.md").read_text()
    assert "decision_result.yaml" in md

def test_g8_gm_report_lists_feynman_artifacts(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    generate_gm_report(run_id, format="markdown")
    md = (run_dir / "gm_report.md").read_text()
    assert "feynman_result.yaml" in md

def test_g8_gm_report_completed_when_required_results_exist(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    
    # need evidence and delivery completed
    (run_dir / "evidence_packet" / "artifact_index.yaml").write_text("{}")
    (run_dir / "evidence_packet" / "validation_summary.yaml").write_text("{}")
    build_delivery_packet(run_id)
    
    generate_gm_report(run_id, format="yaml")
    generate_gm_report(run_id, format="markdown")
    
    gm_yaml = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    gm_md = (run_dir / "gm_report.md").read_text()
    
    assert gm_yaml.get("status") == "completed"
    
    g8 = gm_yaml.get("g8_controls", {})
    assert g8
    assert g8.get("decision_controlled_mode") == "explicit"
    assert g8.get("feynman_controlled_mode") == "explicit"
    assert g8.get("automatic_decision_market_enabled") is False
    assert g8.get("automatic_feynman_executor_enabled") is False
    assert g8.get("real_runtime_used") is False
    
    assert "decision" in gm_md.lower()
    assert "feynman" in gm_md.lower()
    assert "explicit" in gm_md.lower()
    assert "automatic" in gm_md.lower()
    assert "not enabled" in gm_md.lower() or "disabled" in gm_md.lower()
    assert "awaiting_decision" not in gm_md
    assert "awaiting_feynman" not in gm_md

def test_g8_delivery_packet_next_action_is_not_stale_g6_text(fake_run):
    run_id, run_dir = fake_run
    (run_dir / "decision" / "T1").mkdir(parents=True)
    (run_dir / "decision" / "T1" / "decision_result.yaml").write_text("status: completed\n")
    (run_dir / "feynman" / "T2").mkdir(parents=True)
    (run_dir / "feynman" / "T2" / "feynman_result.yaml").write_text("status: completed\n")
    
    (run_dir / "evidence_packet" / "artifact_index.yaml").write_text("{}")
    (run_dir / "evidence_packet" / "validation_summary.yaml").write_text("{}")
    
    build_delivery_packet(run_id)
    
    packet = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    
    # Assert it doesn't contain the stale text
    delivery_text = (run_dir / "delivery_packet.yaml").read_text()
    assert "Ready for Codex G6 review" not in delivery_text
    assert "Codex G6" not in delivery_text
    
    # Assert next_actions has the expected updated generic or phase-aware text
    next_actions = packet.get("next_actions", [])
    if next_actions:
        assert any("Codex acceptance" in action or "G8" in action for action in next_actions)
        assert not any("G6" in action for action in next_actions)
