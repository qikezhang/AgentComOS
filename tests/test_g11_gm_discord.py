import pytest
import os
import yaml
from pathlib import Path
from agentcomos.gm_discord.ingest import ingest_message
from agentcomos.gm_discord.status import get_gm_discord_status
from agentcomos.gm_discord.audit import generate_audit
from agentcomos.gm_discord.parser import parse_message

from agentcomos.controller.state import get_run_dir
import shutil

def test_g11_ingest_requires_fake(tmp_path):
    run_id = "OI-G11-INGEST-FAKE"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M1\ncontent: status")
    
    with pytest.raises(ValueError, match="Only fake adapter is allowed"):
        ingest_message(run_id, str(msg_file), is_fake=False)

def test_g11_ingest_redacts_secrets_and_creates_artifact(tmp_path):
    run_id = "OI-G11-INGEST-REDACT"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: MSG-TEST-001\ncontent: \"my DISCORD_TOKEN is 123\"\nchannel_id: 'C1'")
    
    path = ingest_message(run_id, str(msg_file), is_fake=True)
    
    assert os.path.exists(path)
    with open(path, 'r') as f:
        inbound = yaml.safe_load(f)
        
    assert inbound["message_id"] == "MSG-TEST-001"
    assert inbound["content_redacted"] == "<REDACTED>"
    assert inbound["safety"]["secret_detected"] is True
    assert inbound["safety"]["token_present"] is False
    
import uuid

def test_g11_status_and_audit(tmp_path):
    run_id = f"OI-G11-STAT-AUD-{uuid.uuid4().hex[:8]}"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Status before anything
    status = get_gm_discord_status(run_id)
    if status["status"] == "active":
        assert status["inbound_messages"] == 0
    else:
        assert status["status"] == "inactive"
    
    msg_file = tmp_path / "msg.yaml"
    msg_file.write_text("message_id: M1\ncontent: status")
    ingest_message(run_id, str(msg_file), is_fake=True)
    
    parse_message(run_id, "M1")
    
    status = get_gm_discord_status(run_id)
    assert status["status"] == "active"
    assert status["inbound_messages"] == 1
    
    audit_path = generate_audit(run_id)
    assert os.path.exists(audit_path)
    with open(audit_path, 'r') as f:
        content = f.read()
    assert "M1" in content
    assert "GM Discord Audit" in content
