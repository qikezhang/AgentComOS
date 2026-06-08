from datetime import datetime, timezone
from agentcomos.opencode.availability import is_opencode_available
from agentcomos.opencode.commands import build_opencode_run_attach_command
from agentcomos.opencode.jobs import get_job_id, write_job, get_opencode_logs_dir
from agentcomos.opencode.runtime_status import write_runtime_status

from agentcomos.controller.state import get_run_dir

def submit_real_job(run_id: str, phase: str = "plan") -> str:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    job_id = get_job_id(run_id, 1)
    available = is_opencode_available()
    
    status = "blocked" if not available else "unavailable"
    if not available:
        status = "unavailable"
    
    cmd = build_opencode_run_attach_command(run_id, phase)
    
    logs_dir = get_opencode_logs_dir(run_id)
    stdout_path = logs_dir / f"{job_id}_stdout.log"
    stderr_path = logs_dir / f"{job_id}_stderr.log"
    
    job_data = {
        "job_id": job_id,
        "run_id": run_id,
        "runtime": "real_opencode",
        "phase": phase,
        "status": status,
        "created_by": "controller",
        "submitted_by": "controller",
        "real_opencode_used": True,
        "fake_runtime": False,
        "command": cmd,
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    write_job(run_id, job_id, job_data)
    
    write_runtime_status(run_id, {
        "runtime": "real_opencode",
        "available": available,
        "mode": "real",
        "hostname": "127.0.0.1",
        "port": 4096,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "version": "unknown",
        "reason": "" if available else "opencode not found"
    })
    
    return job_id

from agentcomos.opencode.jobs import read_job

def collect_real_job(run_id: str, job_id: str) -> None:
    job = read_job(run_id, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found in run {run_id}")
    
    status = job.get("status")
    if status in ("unavailable", "blocked"):
        # read-only mode
        return
    # Not implemented fully for real opencode yet.

def recover_real_job(run_id: str, job_id: str) -> None:
    job = read_job(run_id, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found in run {run_id}")

