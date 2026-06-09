from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agentcomos.controller.events import append_event
from agentcomos.controller.state import get_run_dir


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def complete_g7_fake_worker_task(run_id: str, task: dict[str, Any], invocation_path: str) -> dict[str, Any]:
    """
    Deterministic fake worker completion path for G7 Task Frontier.
    This preserves the G4 runtime contract while allowing G7 tests and flow to pass without a real tmux.
    """
    run_dir = get_run_dir(run_id)
    task_id = str(task.get("task_id", "UNKNOWN"))
    
    # 1. Generate required outputs
    output_dir = run_dir / "worker_outputs" / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    done_md = output_dir / "DONE.md"
    done_md.write_text(
        "# DONE\n\n"
        "status: completed\n"
        "worker_runtime: fake_hermes\n"
        "real_hermes_used: false\n"
        "tmux_used: false\n"
        "completed_via: g7_fake_worker_contract\n",
        encoding="utf-8"
    )
    
    result_yaml = output_dir / "result.yaml"
    result_yaml.write_text(
        yaml.dump({
            "run_id": run_id,
            "task_id": task_id,
            "worker_runtime": "fake_hermes",
            "status": "completed",
            "real_hermes_used": False,
            "tmux_used": False,
            "completed_via": "g7_fake_worker_contract",
            "summary": "G7 deterministic fake worker completed Task Frontier validation."
        }, sort_keys=False),
        encoding="utf-8"
    )
    
    reasoning_summary = output_dir / "reasoning_summary.md"
    reasoning_summary.write_text(
        "G7 deterministic fake worker contract executed under controller tick --fake. "
        "No real Hermes, no real tmux, and no subagent was used.\n",
        encoding="utf-8"
    )
    
    # 2. Generate worker job artifact
    job_id = f"HWJ-{run_id}-{task_id}-G7"
    job = {
        "job_id": job_id,
        "run_id": run_id,
        "task_id": task_id,
        "runtime": "g7_fake_worker_contract",
        "status": "completed",
        "fake_worker": True,
        "real_hermes_used": False,
        "tmux_used": False,
        "completed_via": "g7_fake_worker_contract",
        "started_at": _now(),
        "completed_at": _now(),
        "failure_reason": None,
        "required_outputs": task.get("evidence_required", []),
    }
    
    jobs_dir = run_dir / "worker_jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    job_path = jobs_dir / f"{job_id}.yaml"
    job_path.write_text(yaml.dump(job, sort_keys=False), encoding="utf-8")
    
    # Emit events
    append_event(run_id, "worker.job.started", {"job_id": job_id, "shim": "g7_fake_worker_contract"})
    append_event(run_id, "worker.output.detected", {
        "job_id": job_id,
        "missing": [],
        "present": [str(p.relative_to(output_dir)) for p in output_dir.iterdir() if p.is_file()],
        "all_required_present": True
    })
    append_event(run_id, "worker.job.completed", {"job_id": job_id})
    
    return {"job_id": job_id, "invocation": invocation_path}
