from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from agentcomos.frontier.builder import build_task_frontier, read_task_frontier, write_task_frontier
from agentcomos.frontier.dependencies import resolve_task_dependencies
from agentcomos.frontier.executor import update_task_status
from agentcomos.frontier.scheduler import next_ready_task
from agentcomos.frontier.status import generate_frontier_status, list_frontier_tasks
from agentcomos.program.builder import build_operating_program


RUN_ID = "OI-TECHAI8-001"


def make_program_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(yaml.dump({"run_id": RUN_ID, "state": "created"}, sort_keys=False), encoding="utf-8")
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")
    (run_dir / "operating_intent.yaml").write_text(
        yaml.dump({"intent_id": RUN_ID, "goal": "Grow techai8.com to $100/day revenue."}, sort_keys=False),
        encoding="utf-8",
    )
    build_operating_program(RUN_ID)
    return run_dir


def event_types(run_dir: Path) -> list[str]:
    return [json.loads(line)["type"] for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frontier_build_generates_task_frontier(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_program_run(tmp_path)

    frontier = build_task_frontier(RUN_ID)

    assert frontier["frontier_id"] == f"TF-{RUN_ID}"
    assert frontier["status"] == "active"
    assert (run_dir / "task_frontier.yaml").exists()
    assert "frontier.build.completed" in event_types(run_dir)


def test_frontier_contains_required_tasks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)

    frontier = build_task_frontier(RUN_ID)
    tasks = {task["task_id"]: task for task in frontier["tasks"]}

    assert set(tasks) == {"TF-001", "TF-002", "TF-003"}
    assert tasks["TF-001"]["runtime_hint"] == "fake_opencode"
    assert tasks["TF-002"]["invocation_type"] == "worker"
    assert tasks["TF-003"]["evidence_required"] == ["evidence_packet/manifest.yaml", "delivery_packet.yaml", "gm_report.md"]


def test_frontier_dependency_resolution_blocks_dependents(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)

    frontier = build_task_frontier(RUN_ID)
    tasks = {task["task_id"]: task for task in frontier["tasks"]}

    assert tasks["TF-001"]["status"] == "ready"
    assert tasks["TF-002"]["status"] == "blocked"
    assert tasks["TF-003"]["status"] == "blocked"


def test_frontier_dependency_resolution_unblocks_after_completion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)
    frontier = build_task_frontier(RUN_ID)
    frontier["tasks"][0]["status"] = "completed"

    resolved = resolve_task_dependencies(frontier)
    tasks = {task["task_id"]: task for task in resolved["tasks"]}

    assert tasks["TF-002"]["status"] == "ready"
    assert tasks["TF-003"]["status"] == "blocked"


def test_frontier_status_generates_index(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_program_run(tmp_path)
    build_task_frontier(RUN_ID)

    status = generate_frontier_status(RUN_ID)

    assert status["tasks_total"] == 3
    assert status["next_task_id"] == "TF-001"
    assert (run_dir / "task_frontier_index.yaml").exists()
    assert (run_dir / "frontier_status.yaml").exists()


def test_frontier_next_returns_single_ready_task(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)
    frontier = build_task_frontier(RUN_ID)

    task = next_ready_task(frontier)

    assert task is not None
    assert task["task_id"] == "TF-001"
    assert isinstance(task, dict)


def test_frontier_build_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_program_run(tmp_path)
    path = run_dir / "task_frontier.yaml"

    build_task_frontier(RUN_ID)
    first_hash = sha(path)
    first_events = event_types(run_dir)
    build_task_frontier(RUN_ID)
    second_hash = sha(path)
    second_events = event_types(run_dir)

    assert second_hash == first_hash
    assert second_events.count("frontier.build.completed") == first_events.count("frontier.build.completed") == 1


def test_invalid_dependency_fails_safely(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)
    frontier = build_task_frontier(RUN_ID)
    frontier["tasks"][1]["depends_on"] = ["TF-DOES-NOT-EXIST"]
    write_task_frontier(RUN_ID, frontier)

    status = generate_frontier_status(RUN_ID)

    assert status["status"] == "failed"
    assert status["invalid_dependencies"] == [{"task_id": "TF-002", "missing_dependency": "TF-DOES-NOT-EXIST"}]


def test_task_completion_requires_evidence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)
    build_task_frontier(RUN_ID)

    with pytest.raises(ValueError, match="missing required evidence"):
        update_task_status(RUN_ID, "TF-001", "completed")

    frontier = read_task_frontier(RUN_ID)
    task = next(task for task in frontier["tasks"] if task["task_id"] == "TF-001")
    assert task["status"] == "ready"


def test_frontier_list_returns_all_tasks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_program_run(tmp_path)
    build_task_frontier(RUN_ID)

    listed = list_frontier_tasks(RUN_ID)

    assert len(listed["tasks"]) == 3
    assert listed["tasks"][0]["task_id"] == "TF-001"

