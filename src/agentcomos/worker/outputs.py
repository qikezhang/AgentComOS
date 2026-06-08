from __future__ import annotations

from pathlib import Path
from typing import Any


def output_dir_is_inside_run(output_dir: Path, run_dir: Path) -> bool:
    try:
        output_dir.resolve().relative_to((run_dir / "worker_outputs").resolve())
        return True
    except ValueError:
        return False


def detect_required_outputs(output_dir: Path, required_outputs: list[str]) -> dict[str, Any]:
    present = []
    missing = []
    for output in required_outputs:
        if (output_dir / output).exists():
            present.append(output)
        else:
            missing.append(output)

    complete = not missing and (output_dir / "DONE.md").exists()
    return {
        "complete": complete,
        "present": present,
        "missing": missing,
        "done_exists": (output_dir / "DONE.md").exists(),
    }

