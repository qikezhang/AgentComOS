import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir

def get_opencode_jobs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "opencode_jobs"

def get_opencode_logs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "opencode_logs"

def get_opencode_outputs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "opencode_outputs"

def get_job_path(run_id: str, job_id: str) -> Path:
    return get_opencode_jobs_dir(run_id) / f"{job_id}.yaml"

def read_job(run_id: str, job_id: str) -> dict | None:
    path = get_job_path(run_id, job_id)
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def write_job(run_id: str, job_id: str, job_data: dict) -> None:
    path = get_job_path(run_id, job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(job_data, sort_keys=False), encoding="utf-8")

def get_job_id(run_id: str, retry_num: int = 1) -> str:
    return f"OCJ-{run_id}-{retry_num:03d}"
