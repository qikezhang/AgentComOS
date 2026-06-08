import yaml
from pathlib import Path
from agentcomos.controller.state import get_run_dir

def get_runtime_status_path(run_id: str) -> Path:
    return get_run_dir(run_id) / "opencode_runtime_status.yaml"

def read_runtime_status(run_id: str) -> dict | None:
    path = get_runtime_status_path(run_id)
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def write_runtime_status(run_id: str, status_data: dict) -> None:
    path = get_runtime_status_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(status_data, sort_keys=False), encoding="utf-8")
