import pytest
from pathlib import Path
import shutil
from agentcomos.loop.runner import run_loop
from agentcomos.loop.plan import create_loop_plan
from agentcomos.program.builder import build_operating_program
from agentcomos.frontier.builder import build_task_frontier
from agentcomos.controller.state import write_run_status

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def run_dir(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    run_id = "OI-TECHAI8-LOOP-REGRESS"
    d = Path(".agentcomos/runs") / run_id
    d.mkdir(parents=True, exist_ok=True)
    
    src_intent = ROOT / "examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml"
    shutil.copyfile(src_intent, d / "operating_intent.yaml")
    
    write_run_status(run_id, {"run_id": run_id, "state": "executing"})
    
    build_operating_program(run_id)
    build_task_frontier(run_id)
    
    yield d
    shutil.rmtree(d, ignore_errors=True)

def test_loop_runner_rejects_real_runtime(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    with pytest.raises(ValueError, match="only supports --fake runtime"):
        run_loop(run_id, max_ticks=3, fake=False)

def test_loop_summary_states_no_manual_os_or_recursion(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    run_loop(run_id, max_ticks=1, fake=True)
    
    summary = (run_dir / "loop_summary.md").read_text()
    assert "Manual OS: not enabled" in summary
    assert "Worker Evolution: not enabled" in summary
    assert "Auto Versioner: not enabled" in summary
