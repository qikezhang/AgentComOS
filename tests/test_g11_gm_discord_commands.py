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

def test_parse_decision_result_approved(tmp_path):
    run_id = "OI-G11-DEC-1"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M1\ncontent: 'decision result TF-002 approved'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M1")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "decision_result"
    assert cmd["task_id"] == "TF-002"
    assert cmd["requires_confirmation"] is True
    assert cmd["status"] == "parsed"

def test_parse_decision_result_rejected(tmp_path):
    run_id = "OI-G11-DEC-2"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M2\ncontent: 'decision result TF-002 rejected'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M2")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "decision_result"

def test_parse_decision_result_key_value_syntax(tmp_path):
    run_id = "OI-G11-DEC-3"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M3\ncontent: 'decision result task=TF-002 decision=approved'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M3")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "decision_result"
    assert cmd["task_id"] == "TF-002"

def test_parse_feynman_result_passed(tmp_path):
    run_id = "OI-G11-FEYN-1"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M4\ncontent: 'feynman result TF-002 passed'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M4")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "feynman_result"
    assert cmd["task_id"] == "TF-002"

def test_parse_feynman_result_failed(tmp_path):
    run_id = "OI-G11-FEYN-2"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M5\ncontent: 'fail feynman TF-002'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M5")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "feynman_result"
    assert cmd["task_id"] == "TF-002"

def test_parse_feynman_result_key_value_syntax(tmp_path):
    run_id = "OI-G11-FEYN-3"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M6\ncontent: 'feynman result task=TF-002 status=passed'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M6")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "feynman_result"
    assert cmd["task_id"] == "TF-002"

def test_parse_decision_feynman_requires_confirmation(tmp_path):
    run_id = "OI-G11-DEC-REQ"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M7\ncontent: 'decision result TF-002 approved'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M7")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["requires_confirmation"] is True
    assert cmd["safety"]["requires_explicit_confirmation"] is True

def test_unknown_command_blocks_with_reason(tmp_path):
    run_id = "OI-G11-UNK"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M8\ncontent: 'do unknown stuff'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M8")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "unsupported_command"

def test_parse_loop_run_records_max_ticks_fake_real_runtime_used(tmp_path):
    run_id = "OI-G11-LOOP-1"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M9\ncontent: 'loop run OI-TECHAI8-001 max_ticks=3 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M9")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["command_type"] == "loop_run_request"
    assert cmd["max_ticks"] == 3
    assert cmd["fake"] is True
    assert cmd["real_runtime_used"] is False
    assert cmd["safety"]["bounded_loop"] is True

def test_parse_loop_run_missing_max_ticks_blocks(tmp_path):
    run_id = "OI-G11-LOOP-2"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M10\ncontent: 'loop run run=O1 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M10")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "missing_max_ticks"

def test_parse_loop_run_requires_fake(tmp_path):
    run_id = "OI-G11-LOOP-3"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M11\ncontent: 'loop run run=O1 max_ticks=3'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M11")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "fake_required"

def test_parse_loop_run_real_runtime_blocks(tmp_path):
    run_id = "OI-G11-LOOP-4"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M12\ncontent: 'loop run max_ticks=3 real'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M12")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "real_runtime_loop_forbidden"

def test_parse_loop_run_oversized_max_ticks_blocks(tmp_path):
    run_id = "OI-G11-LOOP-5"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M13\ncontent: 'loop run max_ticks=999999 fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M13")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "max_ticks_exceeds_g11_limit"

def test_parse_loop_run_invalid_max_ticks_blocks(tmp_path):
    run_id = "OI-G11-LOOP-6"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M14\ncontent: 'loop run max_ticks=abc fake'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M14")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "invalid_max_ticks"

def test_shell_command_blocked_with_specific_reason(tmp_path):
    run_id = "OI-G11-SH-1"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M15\ncontent: 'run shell: echo hello'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M15")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "prohibited_shell_command"

def test_sudo_systemctl_command_blocked_with_specific_reason(tmp_path):
    run_id = "OI-G11-SH-2"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M16\ncontent: 'sudo systemctl stop thing'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M16")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "sudo_command_blocked"

def test_docker_command_blocked_with_specific_reason(tmp_path):
    run_id = "OI-G11-SH-3"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M17\ncontent: 'docker run something'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M17")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "docker_command_blocked"

def test_ssh_command_blocked_with_specific_reason(tmp_path):
    run_id = "OI-G11-SH-4"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M18\ncontent: 'ssh root@server'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M18")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "ssh_command_blocked"

def test_blocked_command_result_not_completed(tmp_path):
    run_id = "OI-G11-SH-5"
    run_dir = get_run_dir(run_id)
    if run_dir.exists(): shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    msg = tmp_path / "msg.yaml"
    msg.write_text("message_id: M19\ncontent: 'rm -rf /'")
    ingest_message(run_id, str(msg), is_fake=True)
    cmd_path = parse_message(run_id, "M19")
    with open(cmd_path, 'r') as f: cmd = yaml.safe_load(f)
    assert cmd["status"] == "blocked"
    assert cmd["reason"] == "destructive_command_blocked"
    from agentcomos.gm_discord.executor import execute_command
    res_path = execute_command(run_id, "GMC-M19", confirm="explicit")
    with open(res_path, 'r') as f: res = yaml.safe_load(f)
    assert res["status"] == "blocked"
