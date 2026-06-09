from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from agentcomos.cli import app
from agentcomos.worker.fake_hermes import write_fake_outputs
from agentcomos.worker.tmux_pool import TmuxStartResult


RUN_ID = "OI-TECHAI8-001"
runner = CliRunner()


def make_intent(tmp_path: Path) -> Path:
    path = tmp_path / "operating_intent.yaml"
    path.write_text(
        yaml.dump({"intent_id": RUN_ID, "goal": "Grow techai8.com to $100/day revenue."}, sort_keys=False),
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


def make_cli_run(tmp_path: Path):
    result = runner.invoke(app, ["run", "create", "--intent", str(make_intent(tmp_path))])
    assert result.exit_code == 0, result.output


def test_g7_cli_program_and_frontier_commands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_cli_run(tmp_path)

    assert runner.invoke(app, ["program", "build", "--run", RUN_ID]).exit_code == 0
    assert runner.invoke(app, ["program", "status", "--run", RUN_ID]).exit_code == 0
    assert runner.invoke(app, ["frontier", "build", "--run", RUN_ID]).exit_code == 0
    assert runner.invoke(app, ["frontier", "status", "--run", RUN_ID]).exit_code == 0
    assert runner.invoke(app, ["frontier", "list", "--run", RUN_ID]).exit_code == 0
    next_result = runner.invoke(app, ["frontier", "next", "--run", RUN_ID])
    assert next_result.exit_code == 0
    assert "TF-001" in next_result.output


def test_g7_cli_frontier_update_requires_evidence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_cli_run(tmp_path)
    runner.invoke(app, ["program", "build", "--run", RUN_ID])
    runner.invoke(app, ["frontier", "build", "--run", RUN_ID])

    result = runner.invoke(app, ["frontier", "update", "--run", RUN_ID, "--task", "TF-001", "--status", "completed"])

    assert result.exit_code != 0
    assert "missing required evidence" in result.output


def test_g7_cli_controller_tick_fake_integration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_tmux_started(monkeypatch)
    make_cli_run(tmp_path)

    first = runner.invoke(app, ["controller", "tick", "--run", RUN_ID, "--fake"])
    second = runner.invoke(app, ["controller", "tick", "--run", RUN_ID, "--fake"])
    third = runner.invoke(app, ["controller", "tick", "--run", RUN_ID, "--fake"])

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert third.exit_code == 0, third.output
    frontier = yaml.safe_load((tmp_path / ".agentcomos" / "runs" / RUN_ID / "task_frontier.yaml").read_text(encoding="utf-8"))
    assert [task["status"] for task in frontier["tasks"]] == ["completed", "completed", "completed"]


def test_g7_cli_missing_run_fails_without_orphan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["program", "build", "--run", "OI-MISSING"])

    assert result.exit_code != 0
    assert not (tmp_path / ".agentcomos" / "runs" / "OI-MISSING").exists()


def test_g1_to_g6_regression_still_succeeds(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_cli_run(tmp_path)

    tick = runner.invoke(app, ["controller", "tick", "--run", RUN_ID, "--fake"])
    status = runner.invoke(app, ["run", "status", "--run", RUN_ID])

    assert tick.exit_code == 0
    assert status.exit_code == 0
    assert "state: accepted" in status.output


def test_no_agentcomos_runs_artifacts_committed():
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert ".agentcomos/runs/" not in result.stdout
