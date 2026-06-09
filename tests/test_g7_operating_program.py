from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from agentcomos.program.builder import build_operating_program, read_operating_program
from agentcomos.program.status import get_program_status


RUN_ID = "OI-TECHAI8-001"


def make_run(tmp_path: Path, *, intent: bool = True, objective: bool = True) -> Path:
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(yaml.dump({"run_id": RUN_ID, "state": "created"}, sort_keys=False), encoding="utf-8")
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")
    if intent:
        data = {"intent_id": RUN_ID, "created_by": "gm"}
        if objective:
            data["goal"] = "Grow techai8.com to $100/day revenue with AI news and AI tool pages."
        (run_dir / "operating_intent.yaml").write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
    return run_dir


def event_types(run_dir: Path) -> list[str]:
    return [json.loads(line)["type"] for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_program_build_generates_operating_program(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path)

    program = build_operating_program(RUN_ID)

    assert program["program_id"] == f"OP-{RUN_ID}"
    assert program["status"] == "active"
    assert program["source_intent"] == "operating_intent.yaml"
    assert program["constraints"]["no_loop_execution"] is True
    assert program["runtime_policy"]["opencode_default"] == "fake"
    assert (run_dir / "operating_program.yaml").exists()
    assert "program.build.completed" in event_types(run_dir)


def test_program_status_reports_active_program(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    build_operating_program(RUN_ID)

    status = get_program_status(RUN_ID)

    assert status["program_id"] == f"OP-{RUN_ID}"
    assert status["status"] == "active"
    assert status["phase_statuses"]["P1"] == "ready"


def test_program_build_missing_run_fails(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="does not exist"):
        build_operating_program("OI-MISSING")

    assert not (tmp_path / ".agentcomos" / "runs" / "OI-MISSING").exists()


def test_program_build_missing_intent_is_not_completed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path, intent=False)

    with pytest.raises(ValueError, match="missing operating_intent"):
        build_operating_program(RUN_ID)

    program = read_operating_program(RUN_ID)
    assert program is not None
    assert program["status"] == "failed"
    assert program["objective"] is None
    assert "program.build.failed" in event_types(run_dir)
    assert "program.build.completed" not in event_types(run_dir)


def test_program_build_missing_objective_is_not_completed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path, objective=False)

    with pytest.raises(ValueError, match="goal/objective"):
        build_operating_program(RUN_ID)

    program = read_operating_program(RUN_ID)
    assert program is not None
    assert program["status"] == "failed"
    assert program["objective"] is None
    assert "program.build.completed" not in event_types(run_dir)


def test_program_build_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path)
    path = run_dir / "operating_program.yaml"

    build_operating_program(RUN_ID)
    first_hash = sha(path)
    first_events = event_types(run_dir)
    build_operating_program(RUN_ID)
    second_hash = sha(path)
    second_events = event_types(run_dir)

    assert second_hash == first_hash
    assert second_events.count("program.build.completed") == first_events.count("program.build.completed") == 1

