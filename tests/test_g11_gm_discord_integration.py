import pytest
import os
import yaml
from agentcomos.gm_discord.ingest import ingest_message
from agentcomos.gm_discord.parser import parse_message
from agentcomos.gm_discord.executor import execute_command
from agentcomos.controller.runner import handle_run_create
from agentcomos.program.builder import build_operating_program
from agentcomos.frontier.builder import build_task_frontier

from agentcomos.controller.state import get_run_dir
import shutil

def test_g11_execute_status(tmp_path):
    run_id = "OI-G11-EXEC-STAT"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Needs a basic intent to run status
    intent_path = run_dir / "operating_intent.yaml"
    intent_path.write_text("phase: G1\nrun_id: OI-G11-EXEC-1")
    events_path = run_dir / "events.jsonl"
    events_path.write_text('{"event_id": "1"}\n')
    timeline_path = run_dir / "timeline.yaml"
    timeline_path.write_text('events: []')
    status_path = run_dir / "run_status.yaml"
    status_path.write_text('state: created')
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M1\ncontent: status")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M1")
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
        
    res_path = execute_command(run_id, cmd["command_id"])
    with open(res_path, 'r') as f:
        res = yaml.safe_load(f)
    if res["status"] != "completed":
        print(f"Error in execute_status: {res['summary']}")
    assert res["status"] == "completed"

def test_g11_execute_manual_os_requires_confirm(tmp_path):
    run_id = "OI-G11-EXEC-APP"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M2\ncontent: approve manual-os TF-001")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M2")
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
        
    res_path = execute_command(run_id, cmd["command_id"])
    with open(res_path, 'r') as f:
        res = yaml.safe_load(f)
    assert res["status"] == "requires_confirmation"
    
    # with explicit
    res_path = execute_command(run_id, cmd["command_id"], confirm="explicit")
    with open(res_path, 'r') as f:
        res = yaml.safe_load(f)
    # may fail internally because task isn't set up, but status is failed, not requires_conf
    assert res["status"] in ["completed", "failed"]

def test_g11_execute_loop_run(tmp_path):
    run_id = "OI-G11-EXEC-LOOP"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M3\ncontent: loop run fake max_ticks=2")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M3")
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
        
    res_path = execute_command(run_id, cmd["command_id"], confirm="explicit")
    with open(res_path, 'r') as f:
        res = yaml.safe_load(f)
    assert res["status"] in ["completed", "failed"]

def test_execute_loop_run_generates_missing_loop_plan_safely(tmp_path):
    run_id = "OI-G11-INT-LOOP-1"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "operating_intent.yaml").write_text("phase: G11_GM_DISCORD_CONTROLLED_BRIDGE\nrun_id: " + run_id)
    (run_dir / "run_status.yaml").write_text("run_id: " + run_id + "\nstate: created")
    (run_dir / "events.jsonl").write_text("")
    (run_dir / "timeline.yaml").write_text("events: []")

    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M20\ncontent: 'loop run max_ticks=2 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M20")
    res_path = execute_command(run_id, "GMC-M20", confirm="explicit")
    assert (run_dir / "loop_plan.yaml").exists()
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert res["status"] == "completed"

def test_execute_loop_run_with_max_ticks_and_fake_passes(tmp_path):
    run_id = "OI-G11-INT-LOOP-2"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "operating_intent.yaml").write_text("phase: G11_GM_DISCORD_CONTROLLED_BRIDGE\nrun_id: " + run_id)
    (run_dir / "run_status.yaml").write_text("run_id: " + run_id + "\nstate: created")
    (run_dir / "events.jsonl").write_text("")
    (run_dir / "timeline.yaml").write_text("events: []")

    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M21\ncontent: 'loop run max_ticks=3 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M21")
    res_path = execute_command(run_id, "GMC-M21", confirm="explicit")
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert res["status"] == "completed"

def test_execute_loop_run_result_records_ticks_and_stop_reason(tmp_path):
    run_id = "OI-G11-INT-LOOP-3"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "operating_intent.yaml").write_text("phase: G11_GM_DISCORD_CONTROLLED_BRIDGE\nrun_id: " + run_id)
    (run_dir / "run_status.yaml").write_text("run_id: " + run_id + "\nstate: created")
    (run_dir / "events.jsonl").write_text("")
    (run_dir / "timeline.yaml").write_text("events: []")

    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M22\ncontent: 'loop run max_ticks=1 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M22")
    res_path = execute_command(run_id, "GMC-M22", confirm="explicit")
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert "loop" in res
    assert res["loop"]["max_ticks"] == 1
    assert res["loop"]["fake"] is True
    assert res["loop"]["real_runtime_used"] is False
    assert "ticks_executed" in res["loop"]
    assert "stop_reason" in res["loop"]

def test_execute_loop_run_never_uses_real_runtime(tmp_path):
    run_id = "OI-G11-INT-LOOP-4"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M23\ncontent: 'loop run max_ticks=1 real'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M23")
    res_path = execute_command(run_id, "GMC-M23", confirm="explicit")
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert res["status"] == "blocked"
    assert res.get("summary") == "real_runtime_loop_forbidden"

def test_execute_loop_run_without_confirm_blocks(tmp_path):
    run_id = "OI-G11-INT-LOOP-5"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M24\ncontent: 'loop run max_ticks=1 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M24")
    res_path = execute_command(run_id, "GMC-M24")
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert res["status"] == "requires_confirmation"

def test_repeated_blocked_execute_does_not_append_duplicate_event(tmp_path):
    run_id = "OI-G11-INT-IDEM-1"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "events.jsonl").write_text("")
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M25\ncontent: 'rm -rf /'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M25")
    execute_command(run_id, "GMC-M25", confirm="explicit")
    events1 = (run_dir / "events.jsonl").read_text()
    blocked_count1 = events1.count("gm_discord.command.blocked")
    execute_command(run_id, "GMC-M25", confirm="explicit")
    events2 = (run_dir / "events.jsonl").read_text()
    blocked_count2 = events2.count("gm_discord.command.blocked")
    assert blocked_count1 == blocked_count2

def test_repeated_completed_execute_does_not_append_duplicate_event(tmp_path):
    run_id = "OI-G11-INT-IDEM-2"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "events.jsonl").write_text("")
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M26\ncontent: 'status'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M26")
    execute_command(run_id, "GMC-M26")
    events1 = (run_dir / "events.jsonl").read_text()
    completed_count1 = events1.count("gm_discord.command.executed")
    execute_command(run_id, "GMC-M26")
    events2 = (run_dir / "events.jsonl").read_text()
    completed_count2 = events2.count("gm_discord.command.executed")
    assert completed_count1 == completed_count2

def test_gm_discord_audit_updates_when_command_result_changes(tmp_path):
    run_id = "OI-G11-INT-AUDIT-1"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    from agentcomos.gm_discord.audit import generate_audit
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M27\ncontent: 'status'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M27")
    generate_audit(run_id)
    events1 = (run_dir / "events.jsonl").read_text()
    assert "gm_discord.audit.generated" in events1
    execute_command(run_id, "GMC-M27")
    generate_audit(run_id)
    events2 = (run_dir / "events.jsonl").read_text()
    assert "gm_discord.audit.updated" in events2

def test_gm_discord_audit_idempotent_when_no_changes(tmp_path):
    run_id = "OI-G11-INT-AUDIT-2"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    from agentcomos.gm_discord.audit import generate_audit
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M28\ncontent: 'status'")
    ingest_message(run_id, str(msg), is_fake=True)
    parse_message(run_id, "M28")
    generate_audit(run_id)
    events1 = (run_dir / "events.jsonl").read_text()
    update_count1 = events1.count("gm_discord.audit.updated")
    generate_audit(run_id)
    events2 = (run_dir / "events.jsonl").read_text()
    update_count2 = events2.count("gm_discord.audit.updated")
    assert update_count1 == update_count2

def test_gm_discord_status_read_only(tmp_path):
    run_id = "OI-G11-INT-STAT-1"
    from agentcomos.controller.state import get_run_dir
    import shutil, yaml
    from agentcomos.gm_discord.ingest import ingest_message
    from agentcomos.gm_discord.parser import parse_message
    from agentcomos.gm_discord.executor import execute_command
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M29\ncontent: 'status'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M29")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["safety"]["read_only"] is True
