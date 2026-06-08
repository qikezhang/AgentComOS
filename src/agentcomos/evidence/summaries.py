from __future__ import annotations

import yaml
from collections import Counter
from pathlib import Path

import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.worker.jobs import list_worker_jobs

def list_opencode_jobs(run_id: str) -> list[dict]:
    jobs_dir = state.get_run_dir(run_id) / "opencode_jobs"
    if not jobs_dir.exists():
        return []
    jobs = []
    for path in sorted(jobs_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            jobs.append(data)
    return jobs

def generate_events_summary(run_id: str) -> None:
    evts = events.read_events(run_id)
    
    event_counts = Counter(e["type"] for e in evts)
    first_event = min((e["timestamp"] for e in evts), default=None)
    last_event = max((e["timestamp"] for e in evts), default=None)
    
    errors = []
    for e in evts:
        if e.get("payload", {}).get("error") or "failed" in e["type"]:
            errors.append({
                "event_id": e["event_id"],
                "type": e["type"],
                "summary": e.get("payload", {}).get("error", e.get("payload", {}).get("failure_reason", "Unknown error"))
            })
            
    summary = {
        "run_id": run_id,
        "total_events": len(evts),
        "event_types": dict(event_counts),
        "first_event_at": first_event,
        "last_event_at": last_event,
        "has_errors": len(errors) > 0,
        "errors": errors
    }
    
    path = state.get_run_dir(run_id) / "evidence_packet" / "events_summary.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(summary, sort_keys=False), encoding="utf-8")

def generate_runtime_summary(run_id: str) -> None:
    oc_jobs = list_opencode_jobs(run_id)
    worker_jobs = list_worker_jobs(run_id)
    
    oc_fake_used = any(j.get("runtime") == "fake_opencode" or j.get("fake_runtime") for j in oc_jobs)
    oc_real_attempted = any(j.get("runtime") == "real_opencode" or j.get("attempted_real_opencode") for j in oc_jobs)
    oc_real_used = any(j.get("runtime") == "real_opencode" and j.get("status") == "completed" for j in oc_jobs)
    oc_unavailable = sum(1 for j in oc_jobs if j.get("status") == "unavailable")
    oc_failed = sum(1 for j in oc_jobs if j.get("status") == "failed")
    oc_completed = sum(1 for j in oc_jobs if j.get("status") == "completed")
    
    w_fake_used = any(j.get("runtime") in ("fake_hermes", "tmux_fake_hermes") or j.get("fake_worker") for j in worker_jobs)
    w_real_attempted = any(j.get("runtime") == "real_hermes" or j.get("attempted_real_hermes") for j in worker_jobs)
    w_real_used = any(j.get("runtime") == "real_hermes" and j.get("status") == "completed" for j in worker_jobs)
    w_unavailable = sum(1 for j in worker_jobs if j.get("status") == "unavailable")
    w_failed = sum(1 for j in worker_jobs if j.get("status") == "failed")
    w_completed = sum(1 for j in worker_jobs if j.get("status") == "completed")
    w_tmux_used = any(j.get("tmux_used") for j in worker_jobs)
    
    summary = {
        "run_id": run_id,
        "opencode": {
            "fake_opencode_used": oc_fake_used,
            "real_opencode_attempted": oc_real_attempted,
            "real_opencode_used": oc_real_used,
            "unavailable_count": oc_unavailable,
            "failed_count": oc_failed,
            "completed_count": oc_completed
        },
        "hermes": {
            "fake_hermes_used": w_fake_used,
            "real_hermes_attempted": w_real_attempted,
            "real_hermes_used": w_real_used,
            "unavailable_count": w_unavailable,
            "failed_count": w_failed,
            "completed_count": w_completed
        },
        "worker": {
            "tmux_used": w_tmux_used,
            "fake_worker_used": w_fake_used,
            "real_worker_attempted": w_real_attempted
        },
        "safety": {
            "no_loop_execution": True,
            "no_manual_os": True,
            "no_worker_evolution": True,
            "no_auto_versioner": True,
            "no_decision_market_executor": True,
            "no_feynman_executor": True
        }
    }
    
    path = state.get_run_dir(run_id) / "evidence_packet" / "runtime_summary.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(summary, sort_keys=False), encoding="utf-8")
