import pytest
import yaml
import json
import hashlib
from pathlib import Path
from typer.testing import CliRunner
from agentcomos.cli import app

runner = CliRunner()

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def setup_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_id = "OI-TECHAI8-001"
    run_dir = Path(".agentcomos/runs") / run_id
        
    intent_path = ROOT / "examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml"
    res = runner.invoke(app, ["run", "create", "--intent", str(intent_path)])
    assert res.exit_code == 0
    res = runner.invoke(app, ["opencode", "submit", "--run", run_id, "--fake"])
    assert res.exit_code == 0
    res = runner.invoke(app, ["opencode", "collect", "--job", f"OCJ-{run_id}-001"])
    assert res.exit_code == 0
    

    yield run_id, run_dir
    
    if run_dir.exists():
        import shutil
        shutil.rmtree(run_dir)

def test_evidence_build_missing_timeline_does_not_recreate_and_complete(setup_run):
    run_id, run_dir = setup_run
    timeline_path = run_dir / "timeline.yaml"
    timeline_path.unlink()
    
    res = runner.invoke(app, ["evidence", "build", "--run", run_id])
    assert res.exit_code != 0
    print(res.output, repr(res.exception)); assert "Missing timeline.yaml" in res.output
    
    val_path = run_dir / "evidence_packet" / "validation_summary.yaml"
    assert val_path.exists()
    val = yaml.safe_load(val_path.read_text(encoding="utf-8"))
    assert val["checks"]["timeline_present"] == "failed"
    
    man_path = run_dir / "evidence_packet" / "manifest.yaml"
    assert man_path.exists()
    man = yaml.safe_load(man_path.read_text(encoding="utf-8"))
    assert man["status"] != "completed"
    
    assert not timeline_path.exists()

def test_delivery_missing_timeline_evidence_is_not_completed(setup_run):
    run_id, run_dir = setup_run
    (run_dir / "timeline.yaml").unlink()
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    res = runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    dp_path = run_dir / "delivery_packet.yaml"
    assert dp_path.exists()
    dp = yaml.safe_load(dp_path.read_text(encoding="utf-8"))
    assert dp["status"] != "completed"

def test_gm_report_missing_timeline_discloses_incomplete_evidence(setup_run):
    run_id, run_dir = setup_run
    (run_dir / "timeline.yaml").unlink()
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    
    gm_path = run_dir / "gm_report.md"
    assert gm_path.exists()
    text = gm_path.read_text(encoding="utf-8")
    assert "Evidence packet generation failed or missing" in text

def get_hashes(run_dir):
    hashes = {}
    for f in ["evidence_packet/manifest.yaml", "delivery_packet.yaml", "gm_report.md", "gm_report.yaml", "timeline.yaml"]:
        p = run_dir / f
        if p.exists():
            hashes[f] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes

def test_repeated_g6_build_keeps_core_artifact_hashes_stable(setup_run):
    run_id, run_dir = setup_run
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    hashes1 = get_hashes(run_dir)
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "yaml"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    hashes2 = get_hashes(run_dir)
    
    assert hashes1 == hashes2

def test_repeated_g6_build_does_not_duplicate_completed_events(setup_run):
    run_id, run_dir = setup_run
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    def count_completed():
        events_path = run_dir / "events.jsonl"
        c = 0
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if "completed" in line and ("evidence.build" in line or "delivery.build" in line or "gm.report" in line):
                c += 1
        return c
        
    c1 = count_completed()
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    c2 = count_completed()
    
    assert c1 == c2

def test_timeline_is_stable_on_repeated_build(setup_run):
    run_id, run_dir = setup_run
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    h1 = hashlib.sha256((run_dir / "timeline.yaml").read_bytes()).hexdigest()
    
    runner.invoke(app, ["evidence", "build", "--run", run_id])
    runner.invoke(app, ["gm", "report", "--run", run_id, "--format", "markdown"])
    runner.invoke(app, ["delivery", "build", "--run", run_id])
    
    h2 = hashlib.sha256((run_dir / "timeline.yaml").read_bytes()).hexdigest()
    
    assert h1 == h2

