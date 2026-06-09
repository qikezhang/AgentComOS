from __future__ import annotations

from copy import deepcopy
from typing import Any

import yaml

from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.controller.events import append_event, read_events
from agentcomos.controller.state import get_run_dir
from agentcomos.frontier.builder import read_task_frontier, write_task_frontier
from agentcomos.frontier.dependencies import invalid_dependencies, resolve_task_dependencies
from agentcomos.frontier.scheduler import next_ready_task
from agentcomos.program.builder import validate_run_exists


def _has_status_updated(run_id: str, frontier_id: str, fingerprint: str) -> bool:
    for event in read_events(run_id):
        if event.get("type") != "frontier.status.updated":
            continue
        payload = event.get("payload", {})
        if payload.get("frontier_id") == frontier_id and payload.get("fingerprint") == fingerprint:
            return True
    return False


def _has_task_event(run_id: str, event_type: str, task_id: str) -> bool:
    for event in read_events(run_id):
        if event.get("type") == event_type and event.get("payload", {}).get("task_id") == task_id:
            return True
    return False


def _frontier_fingerprint(frontier: dict[str, Any]) -> str:
    import hashlib

    return hashlib.sha256(yaml.dump(frontier, sort_keys=True).encode("utf-8")).hexdigest()


def _evidence_missing(run_id: str, task: dict[str, Any]) -> list[str]:
    run_dir = get_run_dir(run_id)
    missing: list[str] = []
    for rel in task.get("evidence_required") or []:
        if not (run_dir / str(rel)).exists():
            missing.append(str(rel))
    return missing


def generate_frontier_status(run_id: str, append_status_event: bool = True) -> dict[str, Any]:
    validate_run_exists(run_id)
    frontier = read_task_frontier(run_id)
    if not frontier:
        return {"run_id": run_id, "status": "missing", "tasks_total": 0}

    frontier = resolve_task_dependencies(frontier)
    completion_errors = []
    for task in frontier.get("tasks") or []:
        if task.get("status") == "completed":
            missing = _evidence_missing(run_id, task)
            if missing:
                task["status"] = "failed"
                task["failure_reason"] = "completed task missing required evidence: " + ", ".join(missing)
                completion_errors.append({"task_id": task.get("task_id"), "missing": missing})

    if completion_errors and frontier.get("status") != "failed":
        frontier["status"] = "partial"
        frontier["completion_errors"] = completion_errors

    write_task_frontier(run_id, frontier)
    next_task = next_ready_task(frontier)

    counts: dict[str, int] = {}
    by_priority: dict[str, list[str]] = {}
    by_status: dict[str, list[str]] = {}
    index_tasks: dict[str, dict[str, Any]] = {}
    for task in frontier.get("tasks") or []:
        status = str(task.get("status", "unknown"))
        priority = str(task.get("priority", "unknown"))
        counts[status] = counts.get(status, 0) + 1
        by_status.setdefault(status, []).append(str(task.get("task_id")))
        by_priority.setdefault(priority, []).append(str(task.get("task_id")))
        index_tasks[str(task.get("task_id"))] = {
            "status": status,
            "priority": priority,
            "depends_on": task.get("depends_on") or [],
            "runtime_hint": task.get("runtime_hint"),
            "invocation_type": task.get("invocation_type"),
        }

    status_doc = {
        "frontier_id": frontier.get("frontier_id"),
        "run_id": run_id,
        "status": frontier.get("status", "unknown"),
        "tasks_total": len(frontier.get("tasks") or []),
        "counts": counts,
        "next_task_id": next_task.get("task_id") if next_task else None,
        "blocked_tasks": by_status.get("blocked", []),
        "ready_tasks": by_status.get("ready", []),
        "running_tasks": by_status.get("running", []),
        "completed_tasks": by_status.get("completed", []),
        "failed_tasks": by_status.get("failed", []),
        "awaiting_decision_tasks": by_status.get("awaiting_decision", []),
        "awaiting_feynman_tasks": by_status.get("awaiting_feynman", []),
        "awaiting_manual_os_tasks": by_status.get("awaiting_manual_os", []),
        "invalid_dependencies": invalid_dependencies(frontier),
    }
    index_doc = {
        "frontier_id": frontier.get("frontier_id"),
        "run_id": run_id,
        "by_status": by_status,
        "by_priority": by_priority,
        "tasks": index_tasks,
    }

    run_dir = get_run_dir(run_id)
    (run_dir / "frontier_status.yaml").write_text(yaml.dump(status_doc, sort_keys=False), encoding="utf-8")
    (run_dir / "task_frontier_index.yaml").write_text(yaml.dump(index_doc, sort_keys=False), encoding="utf-8")

    fingerprint = _frontier_fingerprint(frontier)
    for task in frontier.get("tasks") or []:
        task_status = str(task.get("status"))
        if task_status in {"ready", "blocked", "awaiting_decision", "awaiting_feynman", "awaiting_manual_os"}:
            event_type = f"frontier.task.{task_status}"
            task_id = str(task.get("task_id"))
            if not _has_task_event(run_id, event_type, task_id):
                append_event(run_id, event_type, {"task_id": task_id, "status": task_status})

    if append_status_event and not _has_status_updated(run_id, str(frontier.get("frontier_id")), fingerprint):
        append_event(run_id, "frontier.status.updated", {
            "frontier_id": frontier.get("frontier_id"),
            "status": status_doc["status"],
            "next_task_id": status_doc["next_task_id"],
            "fingerprint": fingerprint,
        })
        rebuild_timeline_from_events(run_id)

    return deepcopy(status_doc)


def list_frontier_tasks(run_id: str) -> dict[str, Any]:
    validate_run_exists(run_id)
    frontier = read_task_frontier(run_id)
    if not frontier:
        return {"run_id": run_id, "tasks": []}
    return {"run_id": run_id, "tasks": deepcopy(frontier.get("tasks") or [])}
