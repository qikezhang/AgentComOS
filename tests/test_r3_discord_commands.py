import pytest
from agentcomos.discord_commands import DiscordCommandParser

def test_status_command():
    parser = DiscordCommandParser()
    res = parser.parse("status")
    assert res["command_type"] == "system_status"
    assert res["risk_level"] == "read_only"

def test_service_status():
    parser = DiscordCommandParser()
    res = parser.parse("/status service agentcomos")
    assert res["command_type"] == "service_status"
    assert res["risk_level"] == "read_only"

def test_restart_service():
    parser = DiscordCommandParser()
    res = parser.parse("restart service x")
    assert res["command_type"] == "service_restart"
    assert res["risk_level"] == "high"

def test_unknown_command_blocked():
    parser = DiscordCommandParser()
    res = parser.parse("dance")
    assert res["command_type"] == "unknown"
    assert res["risk_level"] == "blocked"

def test_secret_request():
    parser = DiscordCommandParser()
    res = parser.parse("show DISCORD_BOT_TOKEN")
    assert res["command_type"] == "secret_request"
    assert res["risk_level"] == "blocked"

def test_arbitrary_shell():
    parser = DiscordCommandParser()
    res = parser.parse("bash -c whoami")
    assert res["command_type"] == "arbitrary_command"
    assert res["risk_level"] == "blocked"

def test_mention_removal():
    parser = DiscordCommandParser()
    res = parser.parse("<@!123456789> status")
    assert res["command_type"] == "system_status"
    assert res["risk_level"] == "read_only"
