from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agentcomos.controller.state import get_run_dir


def get_worker_jobs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "worker_jobs"


def get_worker_outputs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "worker_outputs"


def get_worker_logs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "worker_logs"


def build_worker_job_id(run_id: str, task_id: str, retry_num: int = 1) -> str:
    return f"HWJ-{run_id}-{task_id}-{retry_num:03d}"


def build_tmux_session_name(run_id: str, task_id: str) -> str:
    return f"agentcomos-{run_id}-{task_id}"


def get_worker_job_path(run_id: str, job_id: str) -> Path:
    return get_worker_jobs_dir(run_id) / f"{job_id}.yaml"


def read_worker_job(run_id: str, job_id: str) -> dict[str, Any] | None:
    path = get_worker_job_path(run_id, job_id)
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def write_worker_job(run_id: str, job_id: str, job: dict[str, Any]) -> None:
    path = get_worker_job_path(run_id, job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(job, sort_keys=False), encoding="utf-8")


def find_worker_job(job_id: str) -> tuple[str, dict[str, Any]] | None:
    root = Path(".agentcomos") / "runs"
    if not root.exists():
        return None
    for path in root.glob(f"*/worker_jobs/{job_id}.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("job_id") == job_id:
            return str(data.get("run_id") or path.parents[1].name), data
    return None


def list_worker_jobs(run_id: str) -> list[dict[str, Any]]:
    jobs_dir = get_worker_jobs_dir(run_id)
    if not jobs_dir.exists():
        return []
    jobs: list[dict[str, Any]] = []
    for path in sorted(jobs_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            jobs.append(data)
    return jobs


def find_job_for_invocation(run_id: str, invocation_id: str) -> dict[str, Any] | None:
    for job in list_worker_jobs(run_id):
        if job.get("invocation_id") == invocation_id:
            return job
    return None

