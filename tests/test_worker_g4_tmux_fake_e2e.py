from pathlib import Path

import pytest
import yaml

from agentcomos.worker.fake_hermes import write_fake_outputs
from agentcomos.worker.jobs import (
    build_tmux_session_name,
    build_worker_job_id,
    get_worker_job_path,
)
from agentcomos.worker.fake_runtime import (
    collect_fake_worker,
    recover_fake_workers,
    start_fake_worker,
    status_fake_worker,
)
from agentcomos.worker.tmux_pool import TmuxStartResult


RUN_ID = "OI-TECHAI8-001"
TASK_ID = "TF-001"
JOB_ID = "HWJ-OI-TECHAI8-001-TF-001-001"


def make_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    run_dir.mkdir(parents=True)
    (run_dir / "run_status.yaml").write_text(
        yaml.dump({"run_id": RUN_ID, "state": "created"}, sort_keys=False),
        encoding="utf-8",
    )
    return run_dir


def make_invocation(tmp_path: Path, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or (
        tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID
    )
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
        "task": {
            "task_id": TASK_ID,
            "goal": "Validate fake worker.",
            "task_type": "research",
        },
        "inputs": ["task_contract.yaml"],
        "output_dir": str(output_dir),
        "required_outputs": ["DONE.md", "result.yaml", "reasoning_summary.md"],
        "stop_conditions": ["required_outputs_exist"],
        "forbidden": ["call_gm", "call_user", "deploy", "merge_git", "real_hermes"],
    }
    path = tmp_path / "invocation.yaml"
    path.write_text(yaml.dump(invocation, sort_keys=False), encoding="utf-8")
    return path


def read_events(run_dir: Path) -> list[dict]:
    events_path = run_dir / "events.jsonl"
    if not events_path.exists():
        return []
    return [yaml.safe_load(line) for line in events_path.read_text(encoding="utf-8").splitlines()]


def fake_tmux_started(monkeypatch):
    def _start(**kwargs):
        write_fake_outputs(kwargs["invocation"])
        return TmuxStartResult(
            status="started",
            session_name=kwargs["session_name"],
            command="tmux new-session -d -s test scripts/fake_hermes_worker.py",
        )

    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _start)


def test_worker_start_generates_worker_job(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)

    job_id = start_fake_worker(invocation, fake=True)

    assert job_id == JOB_ID
    job_path = get_worker_job_path(RUN_ID, job_id)
    job = yaml.safe_load(job_path.read_text(encoding="utf-8"))
    assert job["runtime"] == "tmux_fake_hermes"
    assert job["fake_worker"] is True
    assert job["real_hermes_used"] is False
    assert job["tmux_used"] is True
    assert job["tmux_session_name"] == "agentcomos-OI-TECHAI8-001-TF-001"


def test_worker_start_generates_tmux_session_name():
    assert build_tmux_session_name(RUN_ID, TASK_ID) == "agentcomos-OI-TECHAI8-001-TF-001"
    assert build_worker_job_id(RUN_ID, TASK_ID) == JOB_ID


def test_worker_start_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)

    first = start_fake_worker(invocation, fake=True)
    events_before = (run_dir / "events.jsonl").read_text(encoding="utf-8")
    second = start_fake_worker(invocation, fake=True)

    assert first == second
    assert len(list((run_dir / "worker_jobs").glob("*.yaml"))) == 1
    assert (run_dir / "events.jsonl").read_text(encoding="utf-8") == events_before


def test_worker_status_reads_job_without_mutation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)
    job_id = start_fake_worker(invocation, fake=True)
    job_path = get_worker_job_path(RUN_ID, job_id)
    before = job_path.read_text(encoding="utf-8")

    status_fake_worker(job_id)

    assert job_path.read_text(encoding="utf-8") == before


def test_worker_collect_detects_done_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)
    job_id = start_fake_worker(invocation, fake=True)

    collect_fake_worker(job_id)

    job = yaml.safe_load(get_worker_job_path(RUN_ID, job_id).read_text(encoding="utf-8"))
    assert job["status"] == "completed"
    events = [event["type"] for event in read_events(run_dir)]
    assert "worker.job.created" in events
    assert "worker.tmux.started" in events
    assert "worker.output.detected" in events
    assert "worker.job.completed" in events
    assert "worker.job.collected" in events
    timeline = yaml.safe_load((run_dir / "timeline.yaml").read_text(encoding="utf-8"))
    assert any(event["type"] == "worker.job.completed" for event in timeline["events"])


@pytest.mark.parametrize("missing", ["DONE.md", "result.yaml", "reasoning_summary.md"])
def test_worker_collect_requires_all_required_outputs(tmp_path, monkeypatch, missing):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)
    job_id = start_fake_worker(invocation, fake=True)
    output_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID
    (output_dir / missing).unlink()

    with pytest.raises(ValueError, match="missing required outputs"):
        collect_fake_worker(job_id)

    job = yaml.safe_load(get_worker_job_path(RUN_ID, job_id).read_text(encoding="utf-8"))
    assert job["status"] == "stalled"


def test_worker_collect_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)
    job_id = start_fake_worker(invocation, fake=True)
    collect_fake_worker(job_id)
    result_path = tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID / "result.yaml"
    before = result_path.read_text(encoding="utf-8")

    collect_fake_worker(job_id)

    assert result_path.read_text(encoding="utf-8") == before


def test_worker_missing_invocation_fails(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)

    with pytest.raises(ValueError, match="not found"):
        start_fake_worker(tmp_path / "missing.yaml", fake=True)

    assert not (tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_jobs").exists()


def test_worker_no_real_hermes_usage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)

    job_id = start_fake_worker(invocation, fake=True)
    collect_fake_worker(job_id)

    job = yaml.safe_load(get_worker_job_path(RUN_ID, job_id).read_text(encoding="utf-8"))
    result_path = tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID / "result.yaml"
    result = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    assert job["real_hermes_used"] is False
    assert result["real_hermes_used"] is False


def test_worker_events_are_appended(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)

    job_id = start_fake_worker(invocation, fake=True)
    before = len((run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines())
    collect_fake_worker(job_id)
    after = len((run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines())

    assert after > before


def test_worker_recover_reads_existing_jobs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    fake_tmux_started(monkeypatch)
    job_id = start_fake_worker(invocation, fake=True)

    recovered = recover_fake_workers(RUN_ID)

    assert recovered[0]["job_id"] == job_id
    assert recovered[0]["status"] == "completed"


def test_worker_tmux_unavailable_is_reported_clearly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)

    def _unavailable(**kwargs):
        return TmuxStartResult(
            status="unavailable",
            session_name=kwargs["session_name"],
            reason="tmux not found on PATH",
        )

    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _unavailable)

    job_id = start_fake_worker(invocation, fake=True)

    job = yaml.safe_load(get_worker_job_path(RUN_ID, job_id).read_text(encoding="utf-8"))
    assert job["status"] == "completed"
    assert job["tmux_used"] is False
    assert job["tmux_unavailable"] is True
    assert job["completed_via"] == "fake_no_tmux_contract"
    assert job["real_hermes_used"] is False


def test_worker_output_dir_outside_run_fails(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path, output_dir=tmp_path / "outside")
    data = yaml.safe_load(invocation.read_text(encoding="utf-8"))
    data["run_id"] = RUN_ID
    invocation.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="output_dir must be inside"):
        start_fake_worker(invocation, fake=True)
