from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agentcomos.controller.artifacts import build_timeline
from agentcomos.controller.events import append_event
from agentcomos.controller.state import get_run_dir, read_run_status
from agentcomos.worker.fake_hermes import (
    infer_run_id,
    load_invocation,
    output_dir_from_invocation,
    required_outputs,
    task_id_from_invocation,
)
from agentcomos.worker.jobs import (
    build_tmux_session_name,
    build_worker_job_id,
    find_job_for_invocation,
    find_worker_job,
    get_worker_logs_dir,
    list_worker_jobs,
    read_worker_job,
    write_worker_job,
)
from agentcomos.worker.outputs import detect_required_outputs, output_dir_is_inside_run
from agentcomos.worker.tmux_pool import kill_session, start_real_worker_session, build_real_worker_shell_command
from agentcomos.worker.availability import check_hermes_availability


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _relative_to_run(path: Path, run_id: str) -> str:
    run_dir = get_run_dir(run_id)
    try:
        return str(path.relative_to(run_dir))
    except ValueError:
        return str(path)


def _validate_run_exists(run_id: str) -> None:
    status = read_run_status(run_id)
    if not status or status.get("run_id") != run_id:
        raise ValueError(f"Run {run_id} does not exist. Run create must be executed before worker start.")


def _job_by_id(job_id: str) -> tuple[str, dict[str, Any]]:
    found = find_worker_job(job_id)
    if not found:
        raise ValueError(f"Worker job not found: {job_id}")
    return found


def start_real_worker(invocation_path: Path) -> str:
    invocation = load_invocation(invocation_path)
    if invocation.get("executed_by") != "controller":
        raise ValueError("Worker Invocation must be executed_by: controller")

    run_id = infer_run_id(invocation)
    task_id = task_id_from_invocation(invocation)
    _validate_run_exists(run_id)

    output_dir = output_dir_from_invocation(invocation)
    run_dir = get_run_dir(run_id)
    if not output_dir_is_inside_run(output_dir, run_dir):
        raise ValueError(f"output_dir must be inside {run_dir / 'worker_outputs'}")

    existing = find_job_for_invocation(run_id, str(invocation["invocation_id"]))
    if existing:
        print(f"Existing worker job: {existing['job_id']} status={existing.get('status')}")
        return str(existing["job_id"])

    job_id = build_worker_job_id(run_id, task_id)
    session_name = build_tmux_session_name(run_id, task_id)
    logs_dir = get_worker_logs_dir(run_id)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = logs_dir / f"{job_id}.stdout.log"
    stderr_log = logs_dir / f"{job_id}.stderr.log"
    stdout_log.touch(exist_ok=True)
    stderr_log.touch(exist_ok=True)

    now = _now()
    job = {
        "job_id": job_id,
        "run_id": run_id,
        "task_id": task_id,
        "invocation_id": invocation["invocation_id"],
        "runtime": "real_hermes",
        "status": "created",
        "created_by": "controller",
        "started_by": "controller",
        "fake_worker": False,
        "attempted_real_hermes": True,
        "real_hermes_used": False,
        "tmux_used": False,
        "tmux_session_name": session_name,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "output_dir": str(output_dir),
        "required_outputs": required_outputs(invocation),
        "logs": {
            "stdout": _relative_to_run(stdout_log, run_id),
            "stderr": _relative_to_run(stderr_log, run_id),
        },
        "failure_reason": None,
    }

    is_hermes_available, _ = check_hermes_availability()
    if not is_hermes_available:
        job["status"] = "unavailable"
        job["failure_reason"] = "hermes not found"
        job["attempted_command"] = build_real_worker_shell_command(
            invocation=invocation_path,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
            worktree=Path.cwd(),
        )
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.job.failed", {"job_id": job_id, "reason": "hermes not found"})
        build_timeline(run_id, "worker_unavailable")
        print(f"Worker job unavailable: {job_id} (hermes not found)")
        return job_id

    write_worker_job(run_id, job_id, job)
    append_event(run_id, "worker.job.created", {"job_id": job_id, "task_id": task_id})

    result = start_real_worker_session(
        session_name=session_name,
        invocation=invocation_path,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=Path.cwd(),
    )
    if result.status == "unavailable":
        job["status"] = "unavailable"
        job["failure_reason"] = result.reason
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.job.failed", {"job_id": job_id, "reason": result.reason})
        build_timeline(run_id, "worker_unavailable")
        print(f"Worker job unavailable: {job_id} ({result.reason})")
        return job_id
    if result.status == "failed":
        job["status"] = "failed"
        job["failure_reason"] = result.reason
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.job.failed", {"job_id": job_id, "reason": result.reason})
        build_timeline(run_id, "worker_failed")
        print(f"Worker job failed to start: {job_id} ({result.reason})")
        return job_id

    job["status"] = "running"
    job["tmux_used"] = True
    job["real_hermes_used"] = True
    job["started_at"] = _now()
    job["command"] = result.command
    write_worker_job(run_id, job_id, job)
    append_event(run_id, "worker.tmux.started", {"job_id": job_id, "session": session_name})
    build_timeline(run_id, "worker_running")
    print(f"Worker job started: {job_id}")
    return job_id


def status_real_worker(job_id: str) -> dict[str, Any]:
    run_id, job = _job_by_id(job_id)
    print(yaml.dump(job, sort_keys=False))
    return job


def collect_real_worker(job_id: str) -> dict[str, Any]:
    run_id, job = _job_by_id(job_id)
    if job.get("status") in ("unavailable", "blocked"):
        raise ValueError(f"Cannot collect unavailable worker job {job_id}: {job.get('failure_reason')}")

    output_dir = Path(str(job["output_dir"]))
    detection = detect_required_outputs(output_dir, list(job.get("required_outputs") or []))
    if not detection["complete"]:
        job["status"] = "stalled"
        job["failure_reason"] = "missing required outputs: " + ", ".join(detection["missing"])
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.job.stalled", {"job_id": job_id, **detection})
        build_timeline(run_id, "worker_stalled")
        raise ValueError(f"Worker job {job_id} missing required outputs: {', '.join(detection['missing'])}")

    if job.get("status") != "completed":
        job["status"] = "completed"
        job["completed_at"] = _now()
        job["failure_reason"] = None
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.output.detected", {"job_id": job_id, **detection})
        append_event(run_id, "worker.job.completed", {"job_id": job_id})

    append_event(run_id, "worker.job.collected", {"job_id": job_id})
    build_timeline(run_id, "worker_completed")
    print(f"Worker job collected: {job_id}")
    return job


def kill_real_worker(job_id: str) -> str:
    run_id, job = _job_by_id(job_id)
    message = kill_session(str(job.get("tmux_session_name")))
    if message == "session killed":
        job["status"] = "failed"
        job["failure_reason"] = "killed by controller"
        write_worker_job(run_id, job_id, job)
        append_event(run_id, "worker.job.failed", {"job_id": job_id, "reason": "killed"})
        build_timeline(run_id, "worker_failed")
    print(message)
    return message


def recover_real_workers(run_id: str) -> list[dict[str, Any]]:
    jobs = list_worker_jobs(run_id)
    recovered: list[dict[str, Any]] = []
    for job in jobs:
        # Check runtime routing
        from agentcomos.worker.jobs import detect_job_runtime
        if detect_job_runtime(job) != "real":
            continue

        job_id = str(job["job_id"])
        if job.get("status") in ("unavailable", "blocked"):
            continue

        detection = detect_required_outputs(Path(str(job["output_dir"])), list(job.get("required_outputs") or []))
        if detection["complete"] and job.get("status") != "completed":
            job["status"] = "completed"
            job["completed_at"] = job.get("completed_at") or _now()
            job["failure_reason"] = None
            write_worker_job(run_id, job_id, job)
        recovered.append(job)
    append_event(run_id, "worker.job.recovered", {"job_count": len(recovered)})
    build_timeline(run_id, "worker_recovered")
    print(yaml.dump({"run_id": run_id, "recovered_jobs": recovered}, sort_keys=False))
    return recovered
