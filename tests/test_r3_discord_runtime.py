import pytest
import asyncio
from pathlib import Path
from agentcomos.discord_runtime import DiscordRuntime, serve_discord, DiscordClientFactory
import discord

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

    async def login(self, token):
        pass

    async def close(self):
        self.closed = True

class FakeClientFactory:
    def __init__(self):
        self.client = FakeClient()
    def create(self):
        return self.client

@pytest.fixture
def fake_factory():
    return FakeClientFactory()

def test_runtime_class_exists():
    from agentcomos.discord_runtime import DiscordRuntime
    assert DiscordRuntime

def test_serve_disabled_bot_does_not_create_client(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "false")
    res = asyncio.run(serve_discord(tmp_path, fake_factory))
    assert res["status"] == "unavailable"
    assert res["reason"] == "disabled"
    assert fake_factory.client.started_with_token is None

def test_serve_missing_token_does_not_create_client(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    res = asyncio.run(serve_discord(tmp_path, fake_factory))
    assert res["status"] == "unavailable"
    assert res["reason"] == "token_missing"
    assert fake_factory.client.started_with_token is None

def test_serve_enabled_with_token_calls_client_factory(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    res = asyncio.run(serve_discord(tmp_path, fake_factory))
    assert res["status"] == "started"
    assert fake_factory.client.started_with_token == "real_token"

def test_fake_client_registers_handlers(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    asyncio.run(serve_discord(tmp_path, fake_factory))
    assert "on_message" in fake_factory.client.handlers
    assert "on_ready" in fake_factory.client.handlers

def test_bot_self_message_ignored(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    asyncio.run(serve_discord(tmp_path, fake_factory))
    on_message = fake_factory.client.handlers["on_message"]
    
    msg = FakeMessage("status", bot=True)
    msg.author = fake_factory.client.user
    asyncio.run(on_message(msg))
    
    import yaml
    assert not (tmp_path / "discord_inbound_message.yaml").exists()

def test_real_user_message_passed_into_adapter_pipeline(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    asyncio.run(serve_discord(tmp_path, fake_factory))
    on_message = fake_factory.client.handlers["on_message"]
    
    msg = FakeMessage("status", bot=False)
    asyncio.run(on_message(msg))
    
    import yaml
    assert (tmp_path / "discord_inbound_message.yaml").exists()

def test_runtime_never_calls_subprocess(monkeypatch, tmp_path, fake_factory):
    import subprocess
    import os
    called = False
    def mock_run(*args, **kwargs):
        nonlocal called
        called = True
    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(os, "system", mock_run)
    
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "real_token")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    asyncio.run(serve_discord(tmp_path, fake_factory))
    
    msg = FakeMessage("docker system prune -af", bot=False)
    on_message = fake_factory.client.handlers["on_message"]
    asyncio.run(on_message(msg))
    
    assert called is False

def test_runtime_does_not_persist_token(monkeypatch, tmp_path, fake_factory):
    monkeypatch.setenv("DISCORD_BOT_ENABLED", "true")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "super_secret_token_123")
    monkeypatch.setenv("DISCORD_ALLOW_TEST_PLACEHOLDERS", "true")
    asyncio.run(serve_discord(tmp_path, fake_factory))
    
    msg = FakeMessage("show config DISCORD_BOT_TOKEN=super_secret_token_123", bot=False)
    on_message = fake_factory.client.handlers["on_message"]
    asyncio.run(on_message(msg))
    
    # Check all yaml files
    for f in tmp_path.glob("*.yaml"):
        content = f.read_text(encoding="utf-8")
        assert "super_secret_token_123" not in content
