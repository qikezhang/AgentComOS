import pytest
import os
import yaml
from agentcomos.gm_discord.ingest import ingest_message
from agentcomos.gm_discord.parser import parse_message

from agentcomos.controller.state import get_run_dir
import shutil

def test_g11_parse_status_command(tmp_path):
    run_id = "OI-G11-PARSE-STAT"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M1\ncontent: status")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M1")
    assert os.path.exists(cmd_path)
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "status"
    assert cmd["requires_confirmation"] is False
    assert cmd["safety"]["read_only"] is True

def test_g11_parse_manual_os_approve_command(tmp_path):
    run_id = "OI-G11-PARSE-APP"
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
    assert cmd["command_type"] == "manual_os_approve"
    assert cmd["requires_confirmation"] is True
    assert cmd["status"] == "parsed"

def test_g11_parse_shell_command_blocked(tmp_path):
    run_id = "OI-G11-PARSE-SH"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M3\ncontent: 'run shell: sudo systemctl restart docker'")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    cmd_path = parse_message(run_id, "M3")
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "shell"
    assert cmd["status"] == "blocked"
    assert cmd["safety"]["real_os_execution_allowed"] is False
