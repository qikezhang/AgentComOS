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

def test_delivery_does_not_complete_blocked_g11_command(tmp_path):
    run_id = "OI-G11-REP-1"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    from agentcomos.delivery.builder import build_delivery_packet
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M30\ncontent: 'rm -rf /'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M30")
    execute_command(run_id, "GMC-M30", confirm="explicit")
    build_delivery_packet(run_id)
    dp_path = run_dir / "delivery_packet.yaml"
    with open(dp_path, 'r') as f: dp = yaml.safe_load(f)
    cmd_status = [c["status"] for c in dp.get("g11_controls", {}).get("commands", []) if c["command_id"] == "GMC-M30"]
    assert cmd_status[0] == "blocked"
    assert dp["status"] != "completed"

def test_delivery_discloses_oversized_loop_command(tmp_path):
    run_id = "OI-G11-REP-2"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    from agentcomos.delivery.builder import build_delivery_packet
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M31\ncontent: 'loop run max_ticks=999 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M31")
    build_delivery_packet(run_id)
    dp_path = run_dir / "delivery_packet.yaml"
    with open(dp_path, 'r') as f: dp = yaml.safe_load(f)
    cmd_reason = [c.get("reason") for c in dp.get("g11_controls", {}).get("commands", []) if c["command_id"] == "GMC-M31"]
    assert "max_ticks_exceeds_g11_limit" in cmd_reason[0]

def test_delivery_discloses_requires_confirmation_command(tmp_path):
    run_id = "OI-G11-REP-3"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.delivery.builder import build_delivery_packet
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M32\ncontent: 'approve manual-os TF-001'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M32")
    build_delivery_packet(run_id)
    dp_path = run_dir / "delivery_packet.yaml"
    with open(dp_path, 'r') as f: dp = yaml.safe_load(f)
    cmd_status = [c["status"] for c in dp.get("g11_controls", {}).get("commands", []) if c["command_id"] == "GMC-M32"]
    assert cmd_status[0] == "requires_confirmation"
    assert any("human action required" in a for a in dp.get("next_actions", []))

def test_delivery_includes_blocked_reason(tmp_path):
    run_id = "OI-G11-REP-4"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.delivery.builder import build_delivery_packet
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M33\ncontent: 'sudo rm -rf'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M33")
    build_delivery_packet(run_id)
    dp_path = run_dir / "delivery_packet.yaml"
    with open(dp_path, 'r') as f: dp = yaml.safe_load(f)
    cmd_reason = [c.get("reason") for c in dp.get("g11_controls", {}).get("commands", []) if c["command_id"] == "GMC-M33"]
    assert "sudo_command_blocked" in cmd_reason[0]

def test_gm_report_discloses_blocked_shell_reason(tmp_path):
    run_id = "OI-G11-REP-5"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M34\ncontent: 'run shell: echo hello'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M34")
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    cmd_reason = [c.get("reason") for c in rep.get("gm_discord_bridge", {}).get("commands", []) if c["command_id"] == "GMC-M34"]
    assert "prohibited_shell_command" in cmd_reason[0]

def test_gm_report_discloses_oversized_loop_rejection(tmp_path):
    run_id = "OI-G11-REP-6"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M35\ncontent: 'loop run max_ticks=100 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M35")
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    cmd_reason = [c.get("reason") for c in rep.get("gm_discord_bridge", {}).get("commands", []) if c["command_id"] == "GMC-M35"]
    assert "max_ticks_exceeds_g11_limit" in cmd_reason[0]

def test_gm_report_discloses_requires_confirmation_next_action(tmp_path):
    run_id = "OI-G11-REP-7"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M36\ncontent: 'approve manual-os TF-001'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M36")
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    cmd_na = [c.get("next_action") for c in rep.get("gm_discord_bridge", {}).get("commands", []) if c["command_id"] == "GMC-M36"]
    assert "human must review" in cmd_na[0]

def test_gm_report_does_not_mark_blocked_command_completed(tmp_path):
    run_id = "OI-G11-REP-8"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M37\ncontent: 'rm -rf'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M37")
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    cmd_status = [c.get("status") for c in rep.get("gm_discord_bridge", {}).get("commands", []) if c["command_id"] == "GMC-M37"]
    assert cmd_status[0] == "blocked"

def test_gm_report_discloses_fake_adapter_only(tmp_path):
    run_id = "OI-G11-REP-9"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    assert rep.get("gm_discord_bridge", {}).get("fake_adapter_only") is True

def test_gm_report_discloses_no_real_discord_token_or_send(tmp_path):
    run_id = "OI-G11-REP-10"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm.report import generate_gm_report
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    generate_gm_report(run_id, format="yaml")
    rep_path = run_dir / "gm_report.yaml"
    with open(rep_path, 'r') as f: rep = yaml.safe_load(f)
    bridge = rep.get("gm_discord_bridge", {})
    assert bridge.get("real_discord_token_used") is False
    assert bridge.get("real_discord_message_sent") is False
    assert bridge.get("real_discord_connected") is False
