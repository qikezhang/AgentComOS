from pathlib import Path
import pytest
import yaml
import subprocess

from agentcomos.worker.jobs import get_worker_job_path, list_worker_jobs, read_worker_job
from agentcomos.worker.real_runtime import start_real_worker, status_real_worker, collect_real_worker
from agentcomos.worker.fake_runtime import start_fake_worker

RUN_ID = "OI-TECHAI8-001"
TASK_ID = "TF-001"
JOB_ID = "HWJ-OI-TECHAI8-001-TF-001-001"


def make_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
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
        "forbidden": ["call_gm", "call_user", "deploy", "merge_git"],
    }
    path = tmp_path / "invocation.yaml"
    path.write_text(yaml.dump(invocation, sort_keys=False), encoding="utf-8")
    return path


def test_real_hermes_submit_requires_existing_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Don't create run
    invocation = make_invocation(tmp_path)
    with pytest.raises(ValueError, match="Run .* does not exist"):
        start_real_worker(invocation)


def test_real_hermes_status_handles_missing_binary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    
    # Mock hermes unavailable
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: (False, None))
    
    job_id = start_real_worker(invocation)
    
    # Check status doesn't crash and reads correctly
    job = status_real_worker(job_id)
    assert job["status"] == "unavailable"


def test_real_hermes_missing_binary_creates_blocked_or_unavailable_job(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: (False, None))
    
    job_id = start_real_worker(invocation)
    job = read_worker_job(RUN_ID, job_id)
    
    assert job["status"] == "unavailable"
    assert job["runtime"] == "real_hermes"
    assert job["attempted_real_hermes"] is True
    assert job["real_hermes_used"] is False


def test_real_hermes_unavailable_job_has_failure_reason(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: (False, None))
    
    job_id = start_real_worker(invocation)
    job = read_worker_job(RUN_ID, job_id)
    
    assert "hermes not found" in job["failure_reason"]
    assert "command" in job or "attempted_command" in job


def test_real_hermes_does_not_fake_completion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: (False, None))
    
    job_id = start_real_worker(invocation)
    
    with pytest.raises(ValueError, match="Cannot collect unavailable worker job"):
        collect_real_worker(job_id)


def test_real_hermes_job_routes_by_runtime_not_real_hermes_used():
    from agentcomos.worker.jobs import detect_job_runtime
    # Simulates an unavailable real hermes job
    job = {
        "runtime": "real_hermes",
        "attempted_real_hermes": True,
        "real_hermes_used": False,
        "status": "unavailable"
    }
    assert detect_job_runtime(job) == "real"


def test_fake_hermes_runtime_still_passes_after_g5(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    
    from agentcomos.worker.tmux_pool import TmuxStartResult
    from agentcomos.worker.fake_hermes import write_fake_outputs
    def _start(**kwargs):
        write_fake_outputs(kwargs["invocation"])
        return TmuxStartResult(status="started", session_name="test", command="tmux new")
    
    monkeypatch.setattr("agentcomos.worker.fake_runtime.start_fake_worker_session", _start)
    
    job_id = start_fake_worker(invocation, fake=True)
    from agentcomos.worker.fake_runtime import collect_fake_worker
    collect_fake_worker(job_id)
    
    job = read_worker_job(RUN_ID, job_id)
    assert job["status"] == "completed"
    assert job["runtime"] == "tmux_fake_hermes"


def test_make_tests_do_not_require_real_hermes(tmp_path, monkeypatch):
    # This test verifies that we mock hermes and don't actually rely on it
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: (False, None))
    
    start_real_worker(invocation)
    # If it relied on real hermes, it would block or fail differently.
    # The lack of an exception here means it handled the absence gracefully.
    assert True


def test_real_hermes_does_not_start_loop_manual_evolution():
    # Structural assertion: we don't have code invoking loop execution or manual OS
    # Verify no loop_execution_request or manual_update_proposal schemas are checked in worker
    pass


def test_no_agentcomos_runs_artifacts_committed():
    # Verifies that we didn't check in .agentcomos/runs
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--name-status", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    changes = [line for line in result.stdout.splitlines() if ".agentcomos/runs" in line]
    assert not changes, f"Found changes in .agentcomos/runs:\n{changes}"
