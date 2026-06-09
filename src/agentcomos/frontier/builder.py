from __future__ import annotations

from copy import deepcopy
from typing import Any

import yaml

from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.controller.events import append_event, read_events
from agentcomos.controller.state import get_run_dir
from agentcomos.frontier.dependencies import resolve_task_dependencies
from agentcomos.program.builder import read_operating_program, validate_run_exists


def frontier_path(run_id: str):
    return get_run_dir(run_id) / "task_frontier.yaml"


def _read_yaml(path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return data


def _write_yaml_if_changed(path, data: dict[str, Any]) -> bool:
    text = yaml.dump(data, sort_keys=False)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def _has_event(run_id: str, event_type: str, payload_key: str | None = None, payload_value: str | None = None) -> bool:
    for event in read_events(run_id):
        if event.get("type") != event_type:
            continue
        if payload_key is None:
            return True
        if event.get("payload", {}).get(payload_key) == payload_value:
            return True
    return False


def _append_once(run_id: str, event_type: str, payload: dict[str, Any], key: str | None = None) -> None:
    if key and _has_event(run_id, event_type, key, str(payload.get(key))):
        return
    if not key and _has_event(run_id, event_type):
        return
    append_event(run_id, event_type, payload)


def build_frontier_data(run_id: str) -> dict[str, Any]:
    return {
        "frontier_id": f"TF-{run_id}",
        "run_id": run_id,
        "created_by": "controller",
        "status": "active",
        "tasks": [
            {
                "task_id": "TF-001",
                "title": "Create initial implementation plan",
                "status": "ready",
                "priority": "high",
                "depends_on": [],
                "runtime_hint": "fake_opencode",
                "invocation_type": "opencode",
                "acceptance": ["opencode_project_plan.yaml generated"],
                "evidence_required": ["opencode_outputs/opencode_project_plan.yaml"],
            },
            {
                "task_id": "TF-002",
                "title": "Run fake Hermes worker validation",
                "status": "blocked",
                "priority": "medium",
                "depends_on": ["TF-001"],
                "runtime_hint": "fake_hermes",
                "invocation_type": "worker",
                "acceptance": [
                    "DONE.md generated",
                    "result.yaml generated",
                    "reasoning_summary.md generated",
                ],
                "evidence_required": [
                    "worker_outputs/TF-002/DONE.md",
                    "worker_outputs/TF-002/result.yaml",
                    "worker_outputs/TF-002/reasoning_summary.md",
                ],
            },
            {
                "task_id": "TF-003",
                "title": "Generate evidence delivery and GM report",
                "status": "blocked",
                "priority": "medium",
                "depends_on": ["TF-001", "TF-002"],
                "runtime_hint": "controller",
                "invocation_type": "reporting",
                "acceptance": [
                    "evidence_packet generated",
                    "delivery_packet generated",
                    "gm_report generated",
                ],
                "evidence_required": [
                    "evidence_packet/manifest.yaml",
                    "delivery_packet.yaml",
                    "gm_report.md",
                ],
            },
        ],
    }


def read_task_frontier(run_id: str) -> dict[str, Any] | None:
    path = frontier_path(run_id)
    if not path.exists():
        return None
    return _read_yaml(path)


def write_task_frontier(run_id: str, frontier: dict[str, Any]) -> bool:
    return _write_yaml_if_changed(frontier_path(run_id), frontier)


def build_task_frontier(run_id: str) -> dict[str, Any]:
    validate_run_exists(run_id)
    program = read_operating_program(run_id)
    if not program or program.get("status") != "active":
        append_event(run_id, "frontier.build.started", {"frontier_id": f"TF-{run_id}"})
        append_event(run_id, "frontier.build.failed", {"frontier_id": f"TF-{run_id}", "reason": "active operating_program.yaml required"})
        rebuild_timeline_from_events(run_id)
        raise ValueError(f"Run {run_id} requires active operating_program.yaml before frontier build.")

    expected = resolve_task_dependencies(build_frontier_data(run_id))
    path = frontier_path(run_id)
    if path.exists():
        existing = _read_yaml(path)
        if existing == expected:
            return deepcopy(existing)

    append_event(run_id, "frontier.build.started", {"frontier_id": expected["frontier_id"]})
    write_task_frontier(run_id, expected)
    _append_once(run_id, "frontier.build.completed", {"frontier_id": expected["frontier_id"], "status": "active"}, key="frontier_id")
    for task in expected["tasks"]:
        event_type = "frontier.task.ready" if task["status"] == "ready" else "frontier.task.blocked"
        _append_once(run_id, event_type, {"task_id": task["task_id"], "status": task["status"]}, key="task_id")
    rebuild_timeline_from_events(run_id)
    return deepcopy(expected)

