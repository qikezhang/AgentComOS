from pathlib import Path

import yaml
from typer.testing import CliRunner

from agentcomos.cli import app
from agentcomos.worker.fake_hermes import write_fake_outputs
from agentcomos.worker.tmux_pool import TmuxStartResult


runner = CliRunner()
RUN_ID = "OI-TECHAI8-001"
TASK_ID = "TF-001"
JOB_ID = "HWJ-OI-TECHAI8-001-TF-001-001"


def make_cli_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(
        yaml.dump({"run_id": RUN_ID, "state": "created"}, sort_keys=False),
        encoding="utf-8",
    )
    output_dir = run_dir / "worker_outputs" / TASK_ID
    invocation = {
        "invocation_id": "HWI-TF-001",
        "created_by": "opencode",
        "called_by": "opencode",
        "executed_by": "controller",
        "output_receiver": "opencode",
        "gm_direct_access": False,
        "worker_id": "seo_research_worker",
        "worker_version": "0.1.0",
        "runtime": "hermes_tmux",
        "task": {"task_id": TASK_ID, "goal": "Validate fake worker.", "task_type": "research"},
        "inputs": ["task_contract.yaml"],
        "output_dir": str(output_dir),
        "required_outputs": ["DONE.md", "result.yaml", "reasoning_summary.md"],
        "stop_conditions": ["required_outputs_exist"],
        "forbidden": ["call_gm", "call_user", "deploy", "merge_git", "real_hermes"],
    }
    invocation_path = tmp_path / "invocation.yaml"
    invocation_path.write_text(yaml.dump(invocation, sort_keys=False), encoding="utf-8")
    return invocation_path


def fake_tmux_started(monkeypatch):
    def _start(**kwargs):
        write_fake_outputs(kwargs["invocation"])
        return TmuxStartResult(
            status="started",
            session_name=kwargs["session_name"],
            command="tmux new-session -d -s test scripts/fake_hermes_worker.py",
        )

    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _start)


def test_worker_cli_start_status_collect_list_recover(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    invocation = make_cli_run(tmp_path)
    fake_tmux_started(monkeypatch)

    start = runner.invoke(app, ["worker", "start", "--invocation", str(invocation), "--fake"])
    assert start.exit_code == 0, start.output
    assert JOB_ID in start.output

    status = runner.invoke(app, ["worker", "status", "--job", JOB_ID])
    assert status.exit_code == 0, status.output
    assert "tmux_fake_hermes" in status.output

    collect = runner.invoke(app, ["worker", "collect", "--job", JOB_ID])
    assert collect.exit_code == 0, collect.output
    assert "collected" in collect.output

    listed = runner.invoke(app, ["worker", "list", "--run", RUN_ID])
    assert listed.exit_code == 0, listed.output
    assert JOB_ID in listed.output

    recovered = runner.invoke(app, ["worker", "recover", "--run", RUN_ID])
    assert recovered.exit_code == 0, recovered.output
    assert JOB_ID in recovered.output


def test_worker_cli_requires_fake(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    invocation = make_cli_run(tmp_path)

    result = runner.invoke(app, ["worker", "start", "--invocation", str(invocation)], env={"TERMINAL_WIDTH": "10000", "COLUMNS": "10000", "NO_COLOR": "1", "TERM": "dumb", "_TYPER_STANDARD_TRACEBACK": "1"})
    
    assert result.exit_code != 0
    assert "either --fake or --real" in result.output
