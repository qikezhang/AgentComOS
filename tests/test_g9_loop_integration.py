import pytest
from pathlib import Path
import yaml
import shutil
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.loop.plan import create_loop_plan

runner = CliRunner()

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def run_dir(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    run_id = "OI-TECHAI8-LOOP-INTEGRATION"
    d = Path(".agentcomos/runs") / run_id
    d.mkdir(parents=True, exist_ok=True)
    
    src_intent = ROOT / "examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml"
    shutil.copyfile(src_intent, d / "operating_intent.yaml")
    
    from agentcomos.controller.state import write_run_status
    write_run_status(run_id, {"run_id": run_id, "state": "executing"})
    
    from agentcomos.program.builder import build_operating_program
    from agentcomos.frontier.builder import build_task_frontier
    build_operating_program(run_id)
    build_task_frontier(run_id)
    
    yield d
    shutil.rmtree(d, ignore_errors=True)

def test_loop_integration_updates_artifacts(run_dir: Path):
    run_id = run_dir.name
    create_loop_plan(run_id)
    
    # Run loop
    res = runner.invoke(app, ["loop", "run", "--run", run_id, "--max-ticks", "1", "--fake"])
    assert res.exit_code == 0
    
    # Run reporting tasks (manually invoke controller reporting for simplicity, or just CLI)
    res = runner.invoke(app, ["controller", "tick", "--run", run_id, "--fake"])
    # Note: wait, reporting requires moving state to evidence_verifying, delivery_ready, reported.
    # It's easier to just call the builders directly for the test.
    from agentcomos.evidence.builder import build_evidence_packet
    from agentcomos.delivery.builder import build_delivery_packet
    from agentcomos.gm.report import generate_gm_report
    
    build_evidence_packet(run_id)
    build_delivery_packet(run_id)
    generate_gm_report(run_id, "yaml")
    generate_gm_report(run_id, "markdown")
    
    # 1. Timeline
    timeline = yaml.safe_load((run_dir / "timeline.yaml").read_text())
    loop_events = [e for e in timeline["events"] if e["type"].startswith("loop.")]
    assert len(loop_events) > 0
    
    # 2. Evidence
    manifest = yaml.safe_load((run_dir / "evidence_packet" / "manifest.yaml").read_text())
    assert "loop_plan.yaml" in manifest["inputs"]
    assert "loop_status.yaml" in manifest["inputs"]
    
    artifact_index = yaml.safe_load((run_dir / "evidence_packet" / "artifact_index.yaml").read_text())
    indexed_paths = [a["path"] for a in artifact_index["artifacts"]]
    assert "loop_plan.yaml" in indexed_paths
    assert "loop_status.yaml" in indexed_paths
    assert "loop_trace.yaml" in indexed_paths
    assert "loop_summary.md" in indexed_paths
    
    # 3. Delivery
    delivery = yaml.safe_load((run_dir / "delivery_packet.yaml").read_text())
    assert "loop_status.yaml" in delivery["artifacts"]
    
    # 4. GM Report YAML
    gm_yaml = yaml.safe_load((run_dir / "gm_report.yaml").read_text())
    assert "loop_execution" in gm_yaml
    assert gm_yaml["loop_execution"]["ticks_executed"] == 1
    assert gm_yaml["loop_execution"]["manual_os_enabled"] is False
    assert gm_yaml["loop_execution"]["worker_evolution_enabled"] is False
    assert gm_yaml["loop_execution"]["auto_versioner_enabled"] is False
    assert gm_yaml["loop_execution"]["mode"] == "bounded"
    
    # 5. GM Report MD
    gm_md = (run_dir / "gm_report.md").read_text()
    assert "## Loop Execution Controls" in gm_md
    assert "**Manual OS**: not enabled" in gm_md
    assert "**Worker Evolution**: not enabled" in gm_md
    assert "**Auto Versioner**: not enabled" in gm_md
