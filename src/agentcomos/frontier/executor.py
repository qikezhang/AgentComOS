from __future__ import annotations

from typing import Any

import yaml

from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.controller.events import append_event, read_events
from agentcomos.controller.state import get_run_dir
from agentcomos.frontier.builder import read_task_frontier, write_task_frontier
from agentcomos.frontier.dependencies import resolve_task_dependencies
from agentcomos.frontier.scheduler import next_ready_task
from agentcomos.frontier.status import generate_frontier_status


def _task_by_id(frontier: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    for task in frontier.get("tasks") or []:
        if task.get("task_id") == task_id:
            return task
    return None


def _task_event_seen(run_id: str, event_type: str, task_id: str) -> bool:
    for event in read_events(run_id):
        if event.get("type") == event_type and event.get("payload", {}).get("task_id") == task_id:
            return True
    return False


def _append_task_event_once(run_id: str, event_type: str, task: dict[str, Any], payload: dict[str, Any] | None = None) -> None:
    if _task_event_seen(run_id, event_type, str(task["task_id"])):
        return
    data = {"task_id": task["task_id"], "invocation_type": task.get("invocation_type")}
    if payload:
        data.update(payload)
    append_event(run_id, event_type, data)


def _required_evidence_exists(run_id: str, task: dict[str, Any]) -> tuple[bool, list[str]]:
    run_dir = get_run_dir(run_id)
    missing = [str(rel) for rel in task.get("evidence_required") or [] if not (run_dir / str(rel)).exists()]
    return not missing, missing


def _write_worker_invocation(run_id: str) -> str:
    run_dir = get_run_dir(run_id)
    invocation_id = "HWI-TF-001"
    path = run_dir / "worker_invocations" / f"{invocation_id}.yaml"
    invocation = {
        "invocation_id": invocation_id,
        "created_by": "opencode",
        "called_by": "opencode",
        "executed_by": "controller",
        "output_receiver": "opencode",
        "gm_direct_access": False,
        "worker_id": "seo_research_worker",
        "worker_version": "0.1.0",
        "runtime": "hermes_tmux",
        "task": {
            "task_id": "TF-001",
            "goal": "Run deterministic fake Hermes validation for the G7 frontier.",
            "task_type": "validation",
        },
        "inputs": ["task_frontier.yaml", "runtime_context_bundle.yaml"],
        "output_dir": str(run_dir / "worker_outputs" / "TF-001"),
        "required_outputs": ["DONE.md", "result.yaml", "reasoning_summary.md"],
        "stop_conditions": ["required_outputs_exist", "no_blocking_error"],
        "forbidden": ["call_gm", "call_user", "deploy", "merge_git", "real_hermes"],
    }
    text = yaml.dump(invocation, sort_keys=False)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return str(path)


def _execute_opencode_task(run_id: str, task: dict[str, Any]) -> dict[str, Any]:
    from agentcomos.opencode.fake_runtime import submit_fake_job

    job_id = submit_fake_job(run_id)
    task["invocation_id"] = job_id
    task["runtime_used"] = "fake_opencode"
    ok, missing = _required_evidence_exists(run_id, task)
    if not ok:
        raise ValueError("missing required evidence: " + ", ".join(missing))
    return {"job_id": job_id}


def _execute_worker_task(run_id: str, task: dict[str, Any]) -> dict[str, Any]:
    import time

    from agentcomos.worker.fake_runtime import collect_fake_worker, start_fake_worker

    invocation_path = _write_worker_invocation(run_id)
    job_id = start_fake_worker(get_run_dir(run_id) / "worker_invocations" / "HWI-TF-001.yaml", fake=True)
    task["invocation_id"] = job_id
    task["runtime_used"] = "fake_hermes"
    for _ in range(40):
        ok, _ = _required_evidence_exists(run_id, task)
        if ok:
            break
        time.sleep(0.05)
    collect_fake_worker(job_id)
    ok, missing = _required_evidence_exists(run_id, task)
    if not ok:
        raise ValueError("missing required evidence: " + ", ".join(missing))
    return {"job_id": job_id, "invocation": invocation_path}


def _execute_reporting_task(run_id: str, task: dict[str, Any]) -> dict[str, Any]:
    from agentcomos.delivery.builder import build_delivery_packet
    from agentcomos.evidence.builder import build_evidence_packet
    from agentcomos.gm.report import generate_gm_report

    build_evidence_packet(run_id)
    build_delivery_packet(run_id)
    generate_gm_report(run_id, format="markdown")
    generate_gm_report(run_id, format="yaml")
    task["runtime_used"] = "controller"
    ok, missing = _required_evidence_exists(run_id, task)
    if not ok:
        raise ValueError("missing required evidence: " + ", ".join(missing))
    return {"reports": ["evidence_packet/manifest.yaml", "delivery_packet.yaml", "gm_report.md", "gm_report.yaml"]}


def advance_one_frontier_task(run_id: str) -> dict[str, Any]:
    frontier = read_task_frontier(run_id)
    if not frontier:
        return {"status": "no_op", "reason": "missing_task_frontier"}
    frontier = resolve_task_dependencies(frontier)
    task_snapshot = next_ready_task(frontier)
    if not task_snapshot:
        write_task_frontier(run_id, frontier)
        generate_frontier_status(run_id)
        return {"status": "no_op", "reason": "no_ready_task"}

    task = _task_by_id(frontier, str(task_snapshot["task_id"]))
    if not task:
        return {"status": "no_op", "reason": "selected_task_missing"}

    task["status"] = "running"
    write_task_frontier(run_id, frontier)
    _append_task_event_once(run_id, "frontier.task.started", task)
    rebuild_timeline_from_events(run_id)

    try:
        invocation_type = task.get("invocation_type")
        if invocation_type == "opencode":
            result = _execute_opencode_task(run_id, task)
        elif invocation_type == "worker":
            result = _execute_worker_task(run_id, task)
        elif invocation_type == "reporting":
            result = _execute_reporting_task(run_id, task)
        else:
            raise ValueError(f"Unsupported invocation_type: {invocation_type}")
        task["status"] = "completed"
        task.pop("failure_reason", None)
        task["result"] = result
        write_task_frontier(run_id, resolve_task_dependencies(frontier))
        _append_task_event_once(run_id, "frontier.task.completed", task, {"result": result})
        status_doc = generate_frontier_status(run_id)
        return {"status": "advanced", "task_id": task["task_id"], "frontier_status": status_doc}
    except Exception as exc:
        task["status"] = "failed"
        task["failure_reason"] = str(exc)
        write_task_frontier(run_id, resolve_task_dependencies(frontier))
        _append_task_event_once(run_id, "frontier.task.failed", task, {"failure_reason": str(exc)})
        status_doc = generate_frontier_status(run_id)
        return {"status": "failed", "task_id": task["task_id"], "reason": str(exc), "frontier_status": status_doc}


def update_task_status(run_id: str, task_id: str, status: str) -> dict[str, Any]:
    from agentcomos.frontier.dependencies import ALLOWED_TASK_STATUSES

    if status not in ALLOWED_TASK_STATUSES:
        raise ValueError(f"Invalid task status: {status}")
    frontier = read_task_frontier(run_id)
    if not frontier:
        raise ValueError(f"Run {run_id} missing task_frontier.yaml.")
    task = _task_by_id(frontier, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found.")
    if status == "completed":
        ok, missing = _required_evidence_exists(run_id, task)
        if not ok:
            raise ValueError("Cannot mark completed; missing required evidence: " + ", ".join(missing))
    task["status"] = status
    if status == "failed" and not task.get("failure_reason"):
        task["failure_reason"] = "manually marked failed"
    if status == "skipped" and not task.get("skipped_reason"):
        task["skipped_reason"] = "manually marked skipped"
    write_task_frontier(run_id, resolve_task_dependencies(frontier))
    status_doc = generate_frontier_status(run_id)
    return {"task_id": task_id, "status": status, "frontier_status": status_doc}
