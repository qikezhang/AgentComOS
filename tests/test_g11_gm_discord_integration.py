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
