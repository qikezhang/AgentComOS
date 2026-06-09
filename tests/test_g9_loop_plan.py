import pytest
from pathlib import Path
import yaml
import shutil
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.loop.plan import create_loop_plan, read_loop_plan
from agentcomos.loop.status import get_loop_status

runner = CliRunner()

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def run_dir(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    run_id = "OI-TECHAI8-LOOP"
    d = Path(".agentcomos/runs") / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "operating_intent.yaml").write_text("intent: true") # just to make run exist
    (d / "run_status.yaml").write_text(f"run_id: {run_id}\nstatus: active")
    yield d
    shutil.rmtree(d, ignore_errors=True)

def test_loop_plan_generates_artifact(run_dir: Path):
    run_id = run_dir.name
    res = runner.invoke(app, ["loop", "plan", "--run", run_id])
    assert res.exit_code == 0
    assert (run_dir / "loop_plan.yaml").exists()
    plan = read_loop_plan(run_id)
    assert plan["loop_id"] == f"LOOP-{run_id}"

def test_loop_plan_requires_existing_run():
    res = runner.invoke(app, ["loop", "plan", "--run", "NON_EXISTENT"])
    assert res.exit_code != 0

def test_loop_plan_is_idempotent(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    plan1 = (run_dir / "loop_plan.yaml").read_text()
    create_loop_plan(run_id)
    plan2 = (run_dir / "loop_plan.yaml").read_text()
    assert plan1 == plan2

def test_loop_status_is_read_only(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    # The file doesn't exist yet, get_loop_status should return memory dict
    assert not (run_dir / "loop_status.yaml").exists()
    status = get_loop_status(run_id)
    assert status["status"] == "active"
    assert not (run_dir / "loop_status.yaml").exists()

def test_loop_status_missing_plan_fails(run_dir: Path):
    run_id = run_dir.name
    res = runner.invoke(app, ["loop", "status", "--run", run_id])
    assert res.exit_code != 0

def test_loop_plan_fake_runtime_only_constraints(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    plan = read_loop_plan(run_id)
    assert plan["constraints"]["fake_runtime_only"] is True
    assert plan["constraints"]["no_real_opencode"] is True
