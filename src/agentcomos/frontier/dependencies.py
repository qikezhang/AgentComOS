from __future__ import annotations

from typing import Any


ALLOWED_TASK_STATUSES = {"created", "ready", "blocked", "running", "completed", "failed", "skipped", "awaiting_decision", "awaiting_feynman"}
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
    import yaml
    from agentcomos.controller.state import get_run_dir
    tasks = task_map(frontier)
    invalid = invalid_dependencies(frontier)
    if invalid:
        frontier["status"] = "failed"
        frontier["validation_errors"] = invalid
        return frontier

    run_id = frontier.get("run_id")
    run_dir = get_run_dir(run_id) if run_id else None

    for task in frontier.get("tasks") or []:
        status = str(task.get("status", "created"))
        if status not in ALLOWED_TASK_STATUSES:
            task["status"] = "failed"
            task["failure_reason"] = f"invalid status: {status}"
            continue
        if status in {"completed", "failed", "skipped", "running"}:
            continue
            
        if not dependencies_completed(task, tasks):
            task["status"] = "blocked"
            continue
            
        is_blocked = False
        if task.get("decision_required") and run_dir:
            res_path = run_dir / "decision" / str(task["task_id"]) / "decision_result.yaml"
            if not res_path.exists():
                task["status"] = "awaiting_decision"
                is_blocked = True
            else:
                data = yaml.safe_load(res_path.read_text(encoding="utf-8"))
                if data.get("status") != "completed":
                    task["status"] = "awaiting_decision"
                    is_blocked = True
                    
        if is_blocked:
            continue
            
        if task.get("feynman_required") and run_dir:
            res_path = run_dir / "feynman" / str(task["task_id"]) / "feynman_result.yaml"
            if not res_path.exists():
                task["status"] = "awaiting_feynman"
                is_blocked = True
            else:
                data = yaml.safe_load(res_path.read_text(encoding="utf-8"))
                if data.get("status") != "completed":
                    task["status"] = "awaiting_feynman"
                    is_blocked = True
                elif not data.get("pass"):
                    task["status"] = "blocked"
                    task["failure_reason"] = "feynman check failed"
                    is_blocked = True
                    
        if is_blocked:
            continue
            
        task["status"] = "ready"

    if frontier.get("status") != "failed":
        frontier["status"] = "active"
        frontier.pop("validation_errors", None)
    return frontier
