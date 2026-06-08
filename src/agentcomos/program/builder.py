from __future__ import annotations

from copy import deepcopy
from typing import Any

import yaml

from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.controller.events import append_event, read_events
from agentcomos.controller.state import get_run_dir, read_run_status


def _program_path(run_id: str):
    return get_run_dir(run_id) / "operating_program.yaml"


def _intent_path(run_id: str):
    return get_run_dir(run_id) / "operating_intent.yaml"


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


def validate_run_exists(run_id: str) -> None:
    run_dir = get_run_dir(run_id)
    status = read_run_status(run_id)
    if not run_dir.exists() or not status or status.get("run_id") != run_id:
        raise ValueError(f"Run {run_id} does not exist.")


def build_program_data(run_id: str, intent: dict[str, Any]) -> dict[str, Any]:
    objective = intent.get("goal") or intent.get("objective")
    if not objective:
        raise ValueError("Operating intent missing goal/objective.")
    return {
        "program_id": f"OP-{run_id}",
        "run_id": run_id,
        "created_by": "controller",
        "status": "active",
        "objective": str(objective),
        "source_intent": "operating_intent.yaml",
        "phases": [
            {
                "phase_id": "P1",
                "name": "Plan",
                "status": "ready",
                "acceptance": ["Task frontier generated"],
            },
            {
                "phase_id": "P2",
                "name": "Execute",
                "status": "blocked",
                "acceptance": ["At least one task completed"],
            },
            {
                "phase_id": "P3",
                "name": "Report",
                "status": "blocked",
                "acceptance": ["GM report generated"],
            },
        ],
        "constraints": {
            "no_loop_execution": True,
            "no_recursive_task_expansion": True,
            "no_worker_evolution": True,
            "no_manual_os": True,
            "no_auto_versioner": True,
            "no_decision_market_executor": True,
            "no_feynman_executor": True,
        },
        "runtime_policy": {
            "opencode_default": "fake",
            "hermes_default": "fake",
            "real_runtime_requires_explicit_flag": True,
        },
    }


def build_operating_program(run_id: str) -> dict[str, Any]:
    validate_run_exists(run_id)
    program_path = _program_path(run_id)
    intent_path = _intent_path(run_id)

    if not intent_path.exists():
        if not _has_event(run_id, "program.build.failed"):
            append_event(run_id, "program.build.started", {"program_id": f"OP-{run_id}"})
            failed = {
                "program_id": f"OP-{run_id}",
                "run_id": run_id,
                "created_by": "controller",
                "status": "failed",
                "objective": None,
                "source_intent": "operating_intent.yaml",
                "failure_reason": "missing operating_intent.yaml",
            }
            _write_yaml_if_changed(program_path, failed)
            append_event(run_id, "program.build.failed", {"program_id": f"OP-{run_id}", "reason": "missing operating_intent.yaml"})
            rebuild_timeline_from_events(run_id)
        raise ValueError(f"Run {run_id} missing operating_intent.yaml.")

    intent = _read_yaml(intent_path)
    try:
        program = build_program_data(run_id, intent)
    except ValueError as exc:
        if not _has_event(run_id, "program.build.failed"):
            append_event(run_id, "program.build.started", {"program_id": f"OP-{run_id}"})
            failed = {
                "program_id": f"OP-{run_id}",
                "run_id": run_id,
                "created_by": "controller",
                "status": "failed",
                "objective": None,
                "source_intent": "operating_intent.yaml",
                "failure_reason": str(exc),
            }
            _write_yaml_if_changed(program_path, failed)
            append_event(run_id, "program.build.failed", {"program_id": f"OP-{run_id}", "reason": str(exc)})
            rebuild_timeline_from_events(run_id)
        raise

    if program_path.exists():
        existing = _read_yaml(program_path)
        if existing == program:
            return deepcopy(existing)

    append_event(run_id, "program.build.started", {"program_id": program["program_id"]})
    _write_yaml_if_changed(program_path, program)
    _append_once(run_id, "program.build.completed", {"program_id": program["program_id"], "status": "active"}, key="program_id")
    rebuild_timeline_from_events(run_id)
    return deepcopy(program)


def read_operating_program(run_id: str) -> dict[str, Any] | None:
    path = _program_path(run_id)
    if not path.exists():
        return None
    return _read_yaml(path)

