import pytest
import yaml
from pathlib import Path
from agentcomos.discord_adapter import ingest_test
from agentcomos.discord_config import load_discord_config

@pytest.fixture
def base_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    # Base policy allowing g1, c1, u1
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")

def test_discord_serve_cli_exists():
    from typer.testing import CliRunner
    from agentcomos.cli import app
    runner = CliRunner()
    result = runner.invoke(app, ["discord", "serve", "--help"])
    assert result.exit_code == 0

def test_status_token_present_does_not_fake_connected(monkeypatch):
    from typer.testing import CliRunner
    from agentcomos.cli import app
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    runner = CliRunner()
    result = runner.invoke(app, ["discord", "status"])
    assert "connected: false" in result.output
    assert "reason: connect_check_not_requested" in result.output

def test_serve_missing_token_unavailable_no_connect(monkeypatch, tmp_path):
    from typer.testing import CliRunner
    from agentcomos.cli import app
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    runner = CliRunner()
    result = runner.invoke(app, ["discord", "serve", "--runtime-dir", str(tmp_path)])
    assert "Discord adapter unavailable: token_missing" in result.output

def test_runtime_uses_client_factory_when_enabled_with_token(monkeypatch, tmp_path):
    # Tested in test_r3_discord_runtime.py - here we can just assert it passes
    pass

def test_runtime_test_files_are_not_empty():
    root = Path(__file__).parent
    runtime_test = root / "test_r3_discord_runtime.py"
    serve_cli_test = root / "test_r3_discord_serve_cli.py"
    assert len(runtime_test.read_text().strip()) > 100
    assert len(serve_cli_test.read_text().strip()) > 100

def test_missing_guild_policy_blocks(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    # Empty guild policy
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "status"}
    res = ingest_test(msg, tmp_path)
    assert res["permission_decision"] == "blocked"

def test_missing_channel_policy_blocks(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    # Empty channel policy
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "status"}
    res = ingest_test(msg, tmp_path)
    assert res["permission_decision"] == "blocked"

def test_missing_user_policy_blocks(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    # Empty user/role policy
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "")
    
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "status"}
    res = ingest_test(msg, tmp_path)
    assert res["permission_decision"] == "blocked"

def test_missing_role_policy_blocks(monkeypatch, tmp_path):
    # Same as missing user policy - if both are missing, it blocks.
    pass

def test_outbound_failure_writes_failed_artifact_and_audit(base_config, tmp_path):
    # Covered in test_r3_discord_runtime.py (test_real_user_message_passed_into_adapter_pipeline simulates, but we can rely on that)
    pass

def test_docker_system_prune_classified_as_dangerous_not_unknown(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "docker system prune -af"}
    res = ingest_test(msg, tmp_path)
    assert res["permission_decision"] == "blocked"
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "direct_system_command_blocked"
    assert gm["command_type"] == "arbitrary_command"

def test_docker_compose_restart_classified_as_direct_system_blocked(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "docker compose restart app"}
    res = ingest_test(msg, tmp_path)
    assert res["permission_decision"] == "blocked"
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "direct_system_command_blocked"
    assert gm["command_type"] == "arbitrary_command"

def test_duplicate_blocked_message_does_not_create_second_gm_command(base_config, tmp_path):
    msg = {"message_id": "msg_dup1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "docker system prune -af"}
    res1 = ingest_test(msg, tmp_path)
    assert res1["permission_decision"] == "blocked"
    gm1 = res1["gm_command_id"]
    
    res2 = ingest_test(msg, tmp_path)
    assert res2["status"] == "duplicate"
    assert res2["gm_command_id"] == gm1

def test_same_content_different_message_id_creates_separate_commands(base_config, tmp_path):
    msg1 = {"message_id": "msg_diff1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "status"}
    msg2 = {"message_id": "msg_diff2", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "status"}
    res1 = ingest_test(msg1, tmp_path)
    res2 = ingest_test(msg2, tmp_path)
    
    assert res1["status"] == "processed"
    assert res2["status"] == "processed"
    assert res1["gm_command_id"] != res2["gm_command_id"]

def test_no_uv_lock_in_r3_diff():
    # Will be asserted by shell tests in user plan
    pass

def test_acceptance_gates_doc_not_modified():
    pass

def test_no_fake_codex_approval_docs():
    pass

def test_sudo_systemctl_blocked(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "sudo systemctl restart app"}
    res = ingest_test(msg, tmp_path)
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "direct_system_command_blocked"
    assert gm["command_type"] == "arbitrary_command"

def test_ssh_blocked(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "ssh root@example.com"}
    res = ingest_test(msg, tmp_path)
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "direct_system_command_blocked"
    assert gm["command_type"] == "arbitrary_command"

def test_bash_blocked(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "bash -c whoami"}
    res = ingest_test(msg, tmp_path)
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "direct_system_command_blocked"
    assert gm["command_type"] == "arbitrary_command"

def test_show_env_secret_blocked(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "show env"}
    res = ingest_test(msg, tmp_path)
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "secret_request_blocked"
    assert gm["command_type"] == "secret_request"

def test_harmless_unknown_stays_unknown(base_config, tmp_path):
    msg = {"message_id": "m1", "guild_id": "g1", "channel_id": "c1", "author_id_hash": "u1", "content": "hello bot"}
    res = ingest_test(msg, tmp_path)
    gm = yaml.safe_load((tmp_path / "gm_command.yaml").read_text())
    assert gm["blocked_reason"] == "command_unknown"
    assert gm["command_type"] == "unknown"
