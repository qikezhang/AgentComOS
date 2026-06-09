import os
import yaml
from agentcomos.gm_discord.ingest import ingest_message
from agentcomos.gm_discord.parser import parse_message
from agentcomos.gm_discord.executor import execute_command
from agentcomos.evidence.artifact_index import generate_artifact_index
from agentcomos.delivery.builder import build_delivery_packet
from agentcomos.gm.report import generate_gm_report

from agentcomos.controller.state import get_run_dir
import shutil

def test_g11_reporting_integration(tmp_path):
    run_id = "OI-G11-REP-INT"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    events_path = run_dir / "events.jsonl"
    events_path.write_text('{"event_id": "1", "type": "test.event", "timestamp": "2026-06-09T00:00:00Z"}\n')
    timeline_path = run_dir / "timeline.yaml"
    timeline_path.write_text('events: []')
    manifest_path = run_dir / "evidence_packet" / "manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text('run_id: OI-G11-REP-1')
    status_path = run_dir / "run_status.yaml"
    status_path.write_text('state: created')
    
    # Needs a basic intent
    intent_path = run_dir / "operating_intent.yaml"
    intent_path.write_text("phase: G1\nrun_id: OI-G11-REP-1")
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M1\ncontent: status")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M1")
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
        
    execute_command(run_id, cmd["command_id"])
    
    generate_artifact_index(run_id)
    idx_path = run_dir / "evidence_packet" / "artifact_index.yaml"
    assert idx_path.exists(), "artifact_index.yaml not created"
    with open(idx_path, 'r') as f:
        idx = yaml.safe_load(f)
        paths = [a["path"] for a in idx["artifacts"]]
    
    assert "gm_discord/inbound/M1.yaml" in paths
    assert f"gm_discord/commands/{cmd['command_id']}.yaml" in paths
    assert f"gm_discord/results/{cmd['command_id']}.yaml" in paths
    
    build_delivery_packet(run_id)
    dp_path = run_dir / "delivery_packet.yaml"
    with open(dp_path, 'r') as f:
        dp = yaml.safe_load(f)
        
    assert "g11_controls" in dp
    assert len(dp["g11_controls"]["commands"]) == 1
    assert dp["g11_controls"]["commands"][0]["command_id"] == cmd["command_id"]
    
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f:
        rep = yaml.safe_load(f)
        
    assert "gm_discord_bridge" in rep
    assert rep["gm_discord_bridge"]["controlled_bridge_enabled"] is True
    assert rep["gm_discord_bridge"]["fake_adapter_only"] is True
    assert rep["gm_discord_bridge"]["auto_execute"] is False
