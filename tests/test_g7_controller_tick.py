from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from agentcomos.controller.runner import handle_controller_tick, handle_run_create
from agentcomos.frontier.builder import read_task_frontier
from agentcomos.worker.fake_hermes import write_fake_outputs
from agentcomos.worker.tmux_pool import TmuxStartResult


RUN_ID = "OI-TECHAI8-001"


def make_intent(tmp_path: Path) -> Path:
    path = tmp_path / "operating_intent.yaml"
    path.write_text(
        yaml.dump(
            {
                "intent_id": RUN_ID,
                "created_by": "gm",
                "goal": "Grow techai8.com to $100/day revenue with AI news and AI tool pages.",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def fake_tmux_started(monkeypatch):
    def _start(**kwargs):
        write_fake_outputs(kwargs["invocation"])
        return TmuxStartResult(
            status="started",
            session_name=kwargs["session_name"],
            command="fake-worker-command",
        )

    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _start)


@pytest.fixture
def g7_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    handle_run_create(make_intent(tmp_path))
    return tmp_path / ".agentcomos" / "runs" / RUN_ID


def event_types(run_dir: Path) -> list[str]:
    return [json.loads(line)["type"] for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def task_statuses() -> dict[str, str]:
    frontier = read_task_frontier(RUN_ID)
    return {task["task_id"]: task["status"] for task in frontier["tasks"]}


def test_controller_tick_builds_program_and_frontier(g7_run):
    handle_controller_tick(RUN_ID, fake=True)

    assert (g7_run / "operating_program.yaml").exists()
    assert (g7_run / "task_frontier.yaml").exists()
    assert (g7_run / "frontier_status.yaml").exists()
    assert "program.build.completed" in event_types(g7_run)
    assert "frontier.build.completed" in event_types(g7_run)


def test_controller_tick_advances_at_most_one_task(g7_run):
    handle_controller_tick(RUN_ID, fake=True)

    statuses = task_statuses()
    assert statuses["TF-001"] == "completed"
    assert statuses["TF-002"] == "ready"
    assert statuses["TF-003"] == "blocked"


def test_controller_tick_uses_fake_opencode_only(g7_run):
    handle_controller_tick(RUN_ID, fake=True)

    job = yaml.safe_load((g7_run / "opencode_jobs" / f"OCJ-{RUN_ID}-001.yaml").read_text(encoding="utf-8"))
    assert job["runtime"] == "fake_opencode"
    assert job["fake_runtime"] is True
    assert job["real_opencode_used"] is False


def test_controller_tick_uses_fake_worker_only(g7_run, monkeypatch):
    handle_controller_tick(RUN_ID, fake=True)
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)

    worker_job = yaml.safe_load((g7_run / "worker_jobs" / f"HWJ-{RUN_ID}-TF-001-001.yaml").read_text(encoding="utf-8"))
    result = yaml.safe_load((g7_run / "worker_outputs" / "TF-001" / "result.yaml").read_text(encoding="utf-8"))
    assert worker_job["runtime"] == "tmux_fake_hermes"
    assert worker_job["fake_worker"] is True
    assert worker_job["real_hermes_used"] is False
    assert result["real_hermes_used"] is False


def test_controller_tick_generates_reporting_task(g7_run, monkeypatch):
    handle_controller_tick(RUN_ID, fake=True)
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)

    statuses = task_statuses()
    assert statuses == {"TF-001": "completed", "TF-002": "completed", "TF-003": "completed"}
    assert (g7_run / "evidence_packet" / "manifest.yaml").exists()
    assert (g7_run / "delivery_packet.yaml").exists()
    assert (g7_run / "gm_report.md").exists()


def test_repeated_tick_does_not_duplicate_tasks(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    for _ in range(6):
        handle_controller_tick(RUN_ID, fake=True)

    frontier = read_task_frontier(RUN_ID)
    assert [task["task_id"] for task in frontier["tasks"]] == ["TF-001", "TF-002", "TF-003"]


def test_repeated_tick_does_not_duplicate_completed_events(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    for _ in range(6):
        handle_controller_tick(RUN_ID, fake=True)

    events = event_types(g7_run)
    assert events.count("frontier.task.completed") == 3
    assert events.count("frontier.build.completed") == 1
    assert events.count("program.build.completed") == 1


def test_g7_events_are_appended(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)
    first_count = len(event_types(g7_run))
    handle_controller_tick(RUN_ID, fake=True)
    second_count = len(event_types(g7_run))

    assert second_count > first_count
    assert "frontier.task.started" in event_types(g7_run)
    assert "frontier.task.completed" in event_types(g7_run)


def test_g7_timeline_is_updated(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)

    timeline = yaml.safe_load((g7_run / "timeline.yaml").read_text(encoding="utf-8"))
    types = [event["type"] for event in timeline["events"]]
    assert "program.build.completed" in types
    assert "frontier.task.completed" in types
    assert all("event_id" in event for event in timeline["events"])


def test_controller_tick_does_not_loop_or_recursive_expand(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)
    task_count_after_one = len(read_task_frontier(RUN_ID)["tasks"])
    handle_controller_tick(RUN_ID, fake=True)
    task_count_after_two = len(read_task_frontier(RUN_ID)["tasks"])

    assert task_count_after_one == 3
    assert task_count_after_two == 3


def test_g7_does_not_call_real_opencode_or_hermes(g7_run, monkeypatch):
    def fail_real_opencode(*args, **kwargs):
        raise AssertionError("real OpenCode must not be called by G7")

    def fail_real_hermes(*args, **kwargs):
        raise AssertionError("real Hermes must not be called by G7")

    monkeypatch.setattr("agentcomos.opencode.real_runtime.submit_real_job", fail_real_opencode)
    monkeypatch.setattr("agentcomos.worker.real_runtime.start_real_worker", fail_real_hermes)
    fake_tmux_started(monkeypatch)

    handle_controller_tick(RUN_ID, fake=True)
    handle_controller_tick(RUN_ID, fake=True)

    assert task_statuses()["TF-002"] == "completed"

def test_g7_does_not_start_manual_worker_evolution_auto_versioner(g7_run, monkeypatch):
    fake_tmux_started(monkeypatch)
    handle_controller_tick(RUN_ID, fake=True)

    events = "\n".join(event_types(g7_run))
    assert "manual" not in events
    assert "worker.evolution" not in events
    assert "auto_versioner" not in events
