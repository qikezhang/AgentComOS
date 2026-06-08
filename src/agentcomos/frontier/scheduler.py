from __future__ import annotations

from copy import deepcopy
from typing import Any

from agentcomos.frontier.dependencies import resolve_task_dependencies


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def next_ready_task(frontier: dict[str, Any]) -> dict[str, Any] | None:
    resolved = resolve_task_dependencies(deepcopy(frontier))
    ready = [task for task in resolved.get("tasks") or [] if task.get("status") == "ready"]
    if not ready:
        return None
    ready.sort(key=lambda task: (PRIORITY_ORDER.get(str(task.get("priority")), 99), str(task.get("task_id"))))
    return deepcopy(ready[0])

