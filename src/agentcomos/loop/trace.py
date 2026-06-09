import yaml
from pathlib import Path
from agentcomos.loop.status import get_loop_status

def read_loop_trace(run_id: str) -> dict:
    trace_path = Path(f".agentcomos/runs/{run_id}/loop_trace.yaml")
    if not trace_path.exists():
        raise ValueError(f"loop_trace.yaml missing for run {run_id}")
    return yaml.safe_load(trace_path.read_text(encoding="utf-8"))
