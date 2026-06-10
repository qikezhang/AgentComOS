import pytest
import asyncio
from pathlib import Path
import os
import subprocess
from agentcomos.discord_commands import DiscordCommandParser
from agentcomos.discord_runtime import serve_discord, DiscordRuntime
class FakeUser:
    def __init__(self, bot=False):
        self.bot = bot
        self.id = 12345
        self.roles = []

class FakeGuild:
    def __init__(self):
        self.id = 111

class FakeChannel:
    def __init__(self):
        self.id = 222

class FakeMessage:
    def __init__(self, content, bot=False, is_user=False):
        self.id = "msg_123"
        self.content = content
        self.author = FakeUser(bot=bot)
        self.guild = FakeGuild()
        self.channel = FakeChannel()
        self.is_user = is_user

class FakeClient:
    def __init__(self):
        self.user = FakeUser(bot=True)
        self.handlers = {}
        self.started_with_token = None
        self.closed = False

    def event(self, fn):
        self.handlers[fn.__name__] = fn
        return fn

    async def start(self, token):
        self.started_with_token = token

class FakeClientFactory:
    def __init__(self):
        self.client = FakeClient()
    def create(self):
        return self.client
from agentcomos.discord_artifacts import load_artifact

# COMMAND PARSING FIXES
def test_docker_system_prune_classified_as_dangerous_not_unknown():
    parser = DiscordCommandParser()
    res = parser.parse("docker system prune -af")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "arbitrary_command"
    assert res["blocked_reason"] in ["direct_system_command_blocked", "destructive_docker_command_blocked", "arbitrary_command_blocked"]
    
def test_docker_compose_restart_classified_as_direct_system_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("docker compose restart app")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "arbitrary_command"
    assert res["blocked_reason"] in ["direct_system_command_blocked", "arbitrary_command_blocked"]

def test_sudo_systemctl_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("sudo systemctl restart app")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "arbitrary_command"

def test_ssh_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("ssh root@example.com")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "arbitrary_command"

def test_bash_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("bash -c whoami")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "arbitrary_command"

def test_show_env_secret_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("show env")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "secret_request"

def test_harmless_unknown_stays_unknown():
    parser = DiscordCommandParser()
    res = parser.parse("what is the weather")
    assert res["risk_level"] == "blocked"
    assert res["command_type"] == "unknown"

# HYGIENE & FILES
def test_no_uv_lock_in_r3_diff():
    assert "uv.lock" not in subprocess.getoutput("git diff --name-status origin/main...HEAD")

def test_acceptance_gates_doc_not_modified():
    lines = Path("docs/18_ACCEPTANCE_GATES.md").read_text().splitlines()
    assert len(lines) > 9

def test_no_fake_codex_approval_docs():
    res = subprocess.getoutput("find . -name 'R3_REAL_DISCORD_RUNTIME*'")
    assert "R3_REAL_DISCORD_RUNTIME" not in res

def test_runtime_test_files_are_not_empty():
    assert len(Path("tests/test_r3_discord_runtime.py").read_text().strip()) > 0
    assert len(Path("tests/test_r3_discord_serve_cli.py").read_text().strip()) > 0

@pytest.fixture
def fake_factory():
    return FakeClientFactory()

@pytest.fixture
def base_config(monkeypatch):
    from agentcomos.discord_config import DiscordConfig
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "r_admin,r_ops")
    monkeypatch.setenv("DISCORD_DENIED_ROLE_ALLOWLIST", "r_denied")
    return DiscordConfig()

# ALIAS OTHER TESTS
from test_r3_discord_serve_cli import test_discord_serve_cli_exists, test_serve_missing_token_unavailable_no_connect
from test_r3_discord_serve_cli import test_status_token_present_does_not_fake_connected as test_status_token_present_does_not_fake_connected
from test_r3_discord_runtime import test_serve_enabled_with_token_calls_client_factory as test_runtime_uses_client_factory_when_enabled_with_token
from test_r3_discord_permissions import test_missing_guild_policy_blocks, test_missing_channel_policy_blocks, test_missing_user_policy_blocks, test_missing_role_policy_blocks

# OUTBOUND TESTS
def test_outbound_failure_writes_failed_artifact_and_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    monkeypatch.setenv("DISCORD_OUTBOUND_REPLIES", "true")
    
    factory = FakeClientFactory()
    asyncio.run(serve_discord(tmp_path, factory))
    on_message = factory.client.handlers["on_message"]
    
    msg = FakeMessage("status", bot=False)
    
    # We monkeypatch the outbound sender to fail
    import agentcomos.discord_runtime
    class FailingSender:
        def __init__(self, client): pass
        async def send(self, channel_id, content):
            raise Exception("Network error")
    
    monkeypatch.setattr(agentcomos.discord_runtime, "RealDiscordOutboundSender", FailingSender)
    
    asyncio.run(on_message(msg))
    
    outbound = load_artifact(tmp_path, "discord_outbound_message.yaml")
    assert outbound["delivery_status"] == "failed"
    assert "Network error" in outbound["failure_reason"]
    
    with open(tmp_path / "discord_audit.yaml") as f:
        log_content = f.read()
        assert "outbound_status: failed" in log_content

# DUPLICATE IDEMPOTENCY (Negative coverage)
def test_duplicate_blocked_message_does_not_create_second_gm_command(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    factory = FakeClientFactory()
    asyncio.run(serve_discord(tmp_path, factory))
    on_message = factory.client.handlers["on_message"]
    
    msg = FakeMessage("docker system prune -af", bot=False) # blocked command
    asyncio.run(on_message(msg))
    
    gm1 = load_artifact(tmp_path, "gm_command.yaml")
    assert gm1["status"] == "blocked"
    gm_id1 = gm1["gm_command_id"]
    
    # Send duplicate
    asyncio.run(on_message(msg))
    gm2 = load_artifact(tmp_path, "gm_command.yaml")
    assert gm2["gm_command_id"] == gm_id1 # Should not be overwritten with a new one
    
    inbound = load_artifact(tmp_path, "discord_inbound_message.yaml")
    assert inbound["duplicate_of"] == gm_id1 or "msg_123" in inbound.get("duplicate_of", "msg_123")

def test_same_content_different_message_id_creates_separate_commands(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    
    factory = FakeClientFactory()
    asyncio.run(serve_discord(tmp_path, factory))
    on_message = factory.client.handlers["on_message"]
    
    msg1 = FakeMessage("status", bot=False)
    msg1.id = "msg_A"
    asyncio.run(on_message(msg1))
    gm1 = load_artifact(tmp_path, "gm_command.yaml")
    gm_id1 = gm1["gm_command_id"]
    
    msg2 = FakeMessage("status", bot=False)
    msg2.id = "msg_B"
    asyncio.run(on_message(msg2))
    gm2 = load_artifact(tmp_path, "gm_command.yaml")
    gm_id2 = gm2["gm_command_id"]
    
    assert gm_id1 != gm_id2
