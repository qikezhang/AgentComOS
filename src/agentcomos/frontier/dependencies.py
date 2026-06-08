from __future__ import annotations

from typing import Any


ALLOWED_TASK_STATUSES = {"created", "ready", "blocked", "running", "completed", "failed", "skipped"}
TERMINAL_READY_DEPENDENCY_STATUS = "completed"


def task_map(frontier: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = frontier.get("tasks") or []
    return {str(task.get("task_id")): task for task in tasks if isinstance(task, dict) and task.get("task_id")}


def invalid_dependencies(frontier: dict[str, Any]) -> list[dict[str, str]]:
    tasks = task_map(frontier)
    invalid: list[dict[str, str]] = []
    for task in tasks.values():
        for dep in task.get("depends_on") or []:
            if dep not in tasks:
                invalid.append({"task_id": str(task["task_id"]), "missing_dependency": str(dep)})
    return invalid


def dependencies_completed(task: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> bool:
    for dep in task.get("depends_on") or []:
        if tasks.get(dep, {}).get("status") != TERMINAL_READY_DEPENDENCY_STATUS:
            return False
    return True


def resolve_task_dependencies(frontier: dict[str, Any]) -> dict[str, Any]:
    tasks = task_map(frontier)
    invalid = invalid_dependencies(frontier)
    if invalid:
        frontier["status"] = "failed"
        frontier["validation_errors"] = invalid
        return frontier

    for task in frontier.get("tasks") or []:
        status = str(task.get("status", "created"))
        if status not in ALLOWED_TASK_STATUSES:
            task["status"] = "failed"
            task["failure_reason"] = f"invalid status: {status}"
            continue
        if status in {"completed", "failed", "skipped", "running"}:
            continue
        if dependencies_completed(task, tasks):
            task["status"] = "ready"
        else:
            task["status"] = "blocked"

    if frontier.get("status") != "failed":
        frontier["status"] = "active"
        frontier.pop("validation_errors", None)
    return frontier

