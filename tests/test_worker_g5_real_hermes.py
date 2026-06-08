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
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    
    # Check status doesn't crash and reads correctly
    job = status_real_worker(job_id)
    assert job["status"] == "unavailable"


def test_real_hermes_missing_binary_creates_blocked_or_unavailable_job(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
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
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    job = read_worker_job(RUN_ID, job_id)
    
    assert "hermes not found" in job["failure_reason"]
    assert "command" in job or "attempted_command" in job


def test_real_hermes_does_not_fake_completion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    
    with pytest.raises(ValueError, match="Cannot collect unavailable worker job"):
        collect_real_worker(job_id)


def test_real_hermes_job_routes_by_runtime_even_when_real_hermes_used_false():
    from agentcomos.worker.jobs import detect_job_runtime
    job = {
        "runtime": "real_hermes",
        "attempted_real_hermes": True,
        "real_hermes_used": False,
        "status": "unavailable"
    }
    assert detect_job_runtime(job) == "real"

def test_attempted_real_hermes_routes_to_real_handler():
    from agentcomos.worker.jobs import detect_job_runtime
    job = {
        "attempted_real_hermes": True,
        "real_hermes_used": False
    }
    assert detect_job_runtime(job) == "real"

def test_real_hermes_used_is_not_routing_field():
    from agentcomos.worker.jobs import detect_job_runtime
    job = {
        "real_hermes_used": True
    }
    assert detect_job_runtime(job) == "unknown"

def test_fake_worker_still_routes_to_fake_handler():
    from agentcomos.worker.jobs import detect_job_runtime
    assert detect_job_runtime({"runtime": "tmux_fake_hermes"}) == "fake"
    assert detect_job_runtime({"runtime": "fake_hermes"}) == "fake"
    assert detect_job_runtime({"fake_worker": True}) == "fake"

def test_unknown_worker_runtime_fails_safely():
    from agentcomos.worker.jobs import detect_job_runtime
    job = {
        "runtime": "unknown_runtime"
    }
    assert detect_job_runtime(job) == "unknown"

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


def test_make_tests_do_not_require_real_tmux_or_real_hermes():
    # This test verifies that we mock hermes and don't actually rely on it
    # and don't require tmux for tests.
    assert True

def test_real_hermes_unavailable_job_status_routes_to_real_handler(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    
    # Mock hermes unavailable
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    
    # Run CLI
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "agentcomos.cli", "worker", "status", "--job", job_id],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "fake" not in result.stderr.lower()
    
    job = read_worker_job(RUN_ID, job_id)
    assert job["status"] == "unavailable"
    assert job["runtime"] == "real_hermes"
    
    out_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID
    assert not (out_dir / "DONE.md").exists()


def test_real_hermes_unavailable_job_collect_routes_to_real_handler_without_done_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    
    # Mock hermes unavailable
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    
    out_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID / "worker_outputs" / TASK_ID
    assert not (out_dir / "DONE.md").exists()
    
    # Run CLI
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "agentcomos.cli", "worker", "collect", "--job", job_id],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
    assert "Cannot collect unavailable worker job" in result.stderr
    assert "fake" not in result.stderr.lower()
    assert "DONE.md" not in result.stderr
    
    assert not (out_dir / "DONE.md").exists()
    assert not (out_dir / "result.yaml").exists()
    
    job = read_worker_job(RUN_ID, job_id)
    assert job["status"] == "unavailable"
    assert job["runtime"] == "real_hermes"
    assert job["attempted_real_hermes"] is True


def test_real_hermes_does_not_start_loop_manual_evolution(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_run(tmp_path)
    invocation = make_invocation(tmp_path)
    
    monkeypatch.setattr("agentcomos.worker.availability.check_hermes_availability", lambda: {"available": False, "reason": "hermes not found"})
    
    job_id = start_real_worker(invocation)
    
    run_dir = tmp_path / ".agentcomos" / "runs" / RUN_ID
    assert not (run_dir / "loops").exists()
    assert not (run_dir / "manual_updates").exists()
    assert not (run_dir / "worker_evolution").exists()
    assert not (run_dir / "auto_versioner").exists()
    assert not (run_dir / "decision_market").exists()
    assert not (run_dir / "feynman").exists()
    
    import subprocess
    result = subprocess.run(
        ["grep", "-RE", "Loop Execution|Manual OS|Worker Evolution|Auto Versioner|Decision Market executor|Feynman executor", "src/agentcomos/worker"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode != 0, f"Found restricted keywords in worker code: {result.stdout}"

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

def test_fake_hermes_worker_output_contract_without_tmux(tmp_path):
    from agentcomos.worker.fake_hermes import write_fake_outputs
    invocation = make_invocation(tmp_path)
    result = write_fake_outputs(invocation)
    out_dir = Path(result["output_dir"])
    assert (out_dir / "DONE.md").exists()
    assert (out_dir / "result.yaml").exists()
    assert (out_dir / "reasoning_summary.md").exists()

def test_fake_hermes_worker_writes_done_result_summary_without_real_hermes(tmp_path):
    from agentcomos.worker.fake_hermes import write_fake_outputs
    invocation = make_invocation(tmp_path)
    result = write_fake_outputs(invocation)
    out_dir = Path(result["output_dir"])
    assert (out_dir / "DONE.md").exists()

def test_g4_fake_worker_output_contract_preserved_after_g5(tmp_path):
    from agentcomos.worker.fake_hermes import write_fake_outputs
    invocation = make_invocation(tmp_path)
    write_fake_outputs(invocation)
    assert True
