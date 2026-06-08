import datetime
import yaml
from pathlib import Path
from agentcomos.opencode.jobs import (
    get_job_id,
    get_opencode_logs_dir,
    get_opencode_outputs_dir,
    read_job,
    write_job,
    get_job_path
)
from agentcomos.controller.events import append_event

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def submit_fake_job(run_id: str, retry_num: int = 1) -> str:
    job_id = get_job_id(run_id, retry_num)
    
    # Idempotency check
    existing_job = read_job(run_id, job_id)
    if existing_job and existing_job.get("status") == "completed":
        return job_id

    # Append events
    append_event(run_id, "opencode.job.created", {"job_id": job_id})
    append_event(run_id, "opencode.job.started", {"job_id": job_id})

    # Generate logs
    logs_dir = get_opencode_logs_dir(run_id)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = logs_dir / f"{job_id}.stdout.log"
    stderr_path = logs_dir / f"{job_id}.stderr.log"
    stdout_path.write_text("Fake OpenCode runtime started.\nPlan generated.\n", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")

    # Generate outputs
    outputs_dir = get_opencode_outputs_dir(run_id)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    plan_path = outputs_dir / "opencode_project_plan.yaml"
    plan_data = {
        "run_id": run_id,
        "produced_by": "fake_opencode",
        "phase": "plan",
        "summary": "Fake OpenCode plan generated for G2 validation.",
        "tasks": [
            {
                "task_id": "G2-FAKE-PLAN-001",
                "title": "Validate fake OpenCode runtime integration.",
                "status": "completed"
            }
        ],
        "constraints": {
            "real_opencode_used": False,
            "real_hermes_used": False,
            "tmux_used": False
        },
        "next_actions": [
            "Ready for Codex G2 review."
        ]
    }
    plan_path.write_text(yaml.dump(plan_data, sort_keys=False), encoding="utf-8")

    append_event(run_id, "opencode.output.generated", {"job_id": job_id, "output": "opencode_project_plan.yaml"})

    # Generate job yaml
    now_str = _now()
    job_data = {
        "job_id": job_id,
        "run_id": run_id,
        "runtime": "fake_opencode",
        "phase": "plan",
        "status": "completed",
        "created_by": "controller",
        "submitted_by": "controller",
        "fake_runtime": True,
        "real_opencode_used": False,
        "real_hermes_used": False,
        "started_at": now_str,
        "completed_at": now_str,
        "inputs": [
            "operating_intent.yaml"
        ],
        "outputs": [
            "opencode_outputs/opencode_project_plan.yaml",
            "delivery_packet.yaml"
        ],
        "logs": {
            "stdout": f"opencode_logs/{job_id}.stdout.log",
            "stderr": f"opencode_logs/{job_id}.stderr.log"
        }
    }
    write_job(run_id, job_id, job_data)

    append_event(run_id, "opencode.job.completed", {"job_id": job_id})

    return job_id

def collect_fake_job(run_id: str, job_id: str) -> None:
    job = read_job(run_id, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found for run {run_id}")
    
    if job.get("status") == "completed":
        # Ensure outputs exist
        outputs_dir = get_opencode_outputs_dir(run_id)
        if not (outputs_dir / "opencode_project_plan.yaml").exists():
            raise ValueError(f"Job {job_id} is completed but missing opencode_project_plan.yaml")
        print(f"Collected completed job {job_id}")
    else:
        # For fake runtime, it's always completed immediately, but keeping structure
        pass

def status_fake_job(run_id: str, job_id: str) -> None:
    job = read_job(run_id, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found for run {run_id}")
    print(yaml.dump(job, sort_keys=False))
