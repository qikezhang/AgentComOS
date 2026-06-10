import pytest
from agentcomos.discord_config import DiscordConfig
from agentcomos.discord_permissions import PermissionEvaluator

@pytest.fixture
def base_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token_123")
    monkeypatch.setenv("DISCORD_GUILD_ALLOWLIST", "g1")
    monkeypatch.setenv("DISCORD_CHANNEL_ALLOWLIST", "c1")
    monkeypatch.setenv("DISCORD_USER_ALLOWLIST", "u1")
    monkeypatch.setenv("DISCORD_ROLE_ALLOWLIST", "r_admin,r_ops")
    monkeypatch.setenv("DISCORD_DENIED_ROLE_ALLOWLIST", "r_denied")
    return DiscordConfig()

def test_allowed_passes(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_ops"], "controlled_write")
    assert res.decision == "allowed"

def test_disallowed_channel_blocked(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c2", "u1", ["r_ops"], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "channel_not_allowed"

def test_disallowed_user_blocked(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u2", [], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "user_not_allowed"

def test_denied_role_overrides_allowed_user(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_denied"], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "role_denied"

def test_secret_request_blocked(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_ops"], "secret_request")
    assert res.decision == "blocked"
    assert res.reason == "secret_request_blocked"

def test_arbitrary_command_blocked(base_config):
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_ops"], "arbitrary_command")
    assert res.decision == "blocked"
    assert res.reason == "arbitrary_command_blocked"

def test_missing_guild_policy_blocks(base_config):
    base_config.guild_allowlist = []
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_ops"], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "guild_policy_missing"

def test_missing_channel_policy_blocks(base_config):
    base_config.channel_allowlist = []
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", ["r_ops"], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "channel_policy_missing"

def test_missing_user_policy_blocks(base_config):
    base_config.user_allowlist = []
    base_config.role_allowlist = []
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u1", [], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "user_policy_missing"

def test_missing_role_policy_blocks(base_config):
    base_config.user_allowlist = []
    base_config.role_allowlist = []
    evaluator = PermissionEvaluator(base_config)
    res = evaluator.evaluate("m1", "g1", "c1", "u2", ["r_ops"], "read_only")
    assert res.decision == "blocked"
    assert res.reason == "user_policy_missing"
