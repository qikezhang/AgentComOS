from __future__ import annotations

from typing import Any

from agentcomos.controller.state import get_run_dir
from agentcomos.program.builder import read_operating_program, validate_run_exists


def get_program_status(run_id: str) -> dict[str, Any]:
    validate_run_exists(run_id)
    program = read_operating_program(run_id)
    if not program:
        return {
            "run_id": run_id,
            "status": "missing",
            "program_path": str(get_run_dir(run_id) / "operating_program.yaml"),
        }
    return {
        "run_id": run_id,
        "program_id": program.get("program_id"),
        "status": program.get("status", "unknown"),
        "phase_statuses": {
            phase.get("phase_id"): phase.get("status")
            for phase in program.get("phases", [])
            if isinstance(phase, dict)
        },
        "constraints": program.get("constraints", {}),
        "runtime_policy": program.get("runtime_policy", {}),
    }

