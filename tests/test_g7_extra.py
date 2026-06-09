from __future__ import annotations
import pytest
import yaml
from pathlib import Path
from agentcomos.controller.runner import handle_controller_tick, handle_run_create
from agentcomos.frontier.builder import read_task_frontier
from agentcomos.worker.tmux_pool import TmuxStartResult

RUN_ID = "OI-TECHAI8-001"

def make_intent(tmp_path: Path) -> Path:
    path = tmp_path / "operating_intent.yaml"
    path.write_text(yaml.dump({
        "intent_id": RUN_ID,
        "created_by": "gm",
        "goal": "Grow techai8.com."
    }, sort_keys=False), encoding="utf-8")
    return path

@pytest.fixture
def g7_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    handle_run_create(make_intent(tmp_path))
    return tmp_path / ".agentcomos" / "runs" / RUN_ID

def test_g7_three_tick_flow_completes_tf001_tf002_tf003(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)

    handle_controller_tick(RUN_ID, fake=True)
    assert read_task_frontier(RUN_ID)["tasks"][0]["status"] == "completed"

    handle_controller_tick(RUN_ID, fake=True)
    assert read_task_frontier(RUN_ID)["tasks"][1]["status"] == "completed"
    assert (g7_run / "worker_outputs" / "TF-002" / "DONE.md").exists()

    handle_controller_tick(RUN_ID, fake=True)
    assert read_task_frontier(RUN_ID)["tasks"][2]["status"] == "completed"

    frontier = read_task_frontier(RUN_ID)
    assert all(t["status"] == "completed" for t in frontier["tasks"])

def test_g7_tf002_fake_worker_outputs_are_generated_without_real_tmux(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found on PATH")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    
    assert (g7_run / "worker_outputs" / "TF-002" / "DONE.md").exists()
    assert (g7_run / "worker_outputs" / "TF-002" / "result.yaml").exists()
    assert (g7_run / "worker_outputs" / "TF-002" / "reasoning_summary.md").exists()
    
    job = yaml.safe_load((g7_run / "worker_jobs" / f"HWJ-{RUN_ID}-TF-002-G7.yaml").read_text(encoding="utf-8"))
    assert job["tmux_used"] is False
    assert job["real_hermes_used"] is False

def test_g7_frontier_evidence_required_matches_worker_output_paths(g7_run, monkeypatch):
    handle_controller_tick(RUN_ID, fake=True)
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    handle_controller_tick(RUN_ID, fake=True)
    
    frontier = read_task_frontier(RUN_ID)
    tf002 = next(t for t in frontier["tasks"] if t["task_id"] == "TF-002")
    for ev in tf002["evidence_required"]:
        assert (g7_run / ev).exists()

def test_g7_tick3_reporting_task_runs_after_worker_completed(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    
    assert (g7_run / "evidence_packet" / "manifest.yaml").exists()
    assert (g7_run / "delivery_packet.yaml").exists()
    assert (g7_run / "gm_report.md").exists()

def test_g7_failed_frontier_report_is_not_completed(g7_run, monkeypatch):
    handle_controller_tick(RUN_ID, fake=True)
    def _fail(*args, **kwargs):
        raise ValueError("fatal error")
    monkeypatch.setattr("agentcomos.frontier.fake_worker_contract.complete_g7_fake_worker_task", _fail)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    
    from agentcomos.evidence.builder import build_evidence_packet
    from agentcomos.delivery.builder import build_delivery_packet
    from agentcomos.gm.report import generate_gm_report
    
    build_evidence_packet(RUN_ID)
    build_delivery_packet(RUN_ID)
    generate_gm_report(RUN_ID, "yaml")
    generate_gm_report(RUN_ID, "markdown")
    
    report = yaml.safe_load((g7_run / "gm_report.yaml").read_text(encoding="utf-8"))
    delivery = yaml.safe_load((g7_run / "delivery_packet.yaml").read_text(encoding="utf-8"))
    assert report["status"] != "completed"
    assert delivery["status"] != "completed"
    assert any("TF-002" in text for text in report["failed_tasks_disclosure"])

def test_g7_completed_frontier_report_can_be_completed(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)
    
    report = yaml.safe_load((g7_run / "gm_report.yaml").read_text(encoding="utf-8"))
    delivery = yaml.safe_load((g7_run / "delivery_packet.yaml").read_text(encoding="utf-8"))
    assert report["status"] == "completed"
    assert delivery["status"] == "completed"

def test_g7_no_ready_task_after_all_completed_is_no_op(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    for _ in range(4):
        handle_controller_tick(RUN_ID, fake=True)
    
    frontier = read_task_frontier(RUN_ID)
    assert len(frontier["tasks"]) == 3
    assert all(t["status"] == "completed" for t in frontier["tasks"])

def test_g7_does_not_loop_or_recursive_expand(g7_run, monkeypatch):
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    for _ in range(3):
        handle_controller_tick(RUN_ID, fake=True)
    
    assert len(read_task_frontier(RUN_ID)["tasks"]) == 3
    
def test_g7_does_not_call_real_opencode_or_hermes(g7_run, monkeypatch):
    def _fail_opencode(*args, **kwargs):
        raise AssertionError("called real opencode")
    def _fail_hermes(*args, **kwargs):
        raise AssertionError("called real hermes")
    monkeypatch.setattr("agentcomos.opencode.real_runtime.submit_real_job", _fail_opencode)
    monkeypatch.setattr("agentcomos.worker.real_runtime.start_real_worker", _fail_hermes)
    
    def _unavailable(**kwargs):
        return TmuxStartResult(status="unavailable", session_name=kwargs["session_name"], reason="tmux not found")
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)
    
    for _ in range(3):
        handle_controller_tick(RUN_ID, fake=True)
