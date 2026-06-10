import pytest
from agentcomos.executor_redaction import redact_executor_text, redact_executor_data, contains_secret_like_text

def test_redact_executor_text_tokens():
    raw = "show env DISCORD_BOT_TOKEN=REAL_TOKEN_SHOULD_NOT_APPEAR password=SUPER_SECRET api_key=ABC123"
    redacted = redact_executor_text(raw)
    assert "REAL_TOKEN_SHOULD_NOT_APPEAR" not in redacted
    assert "SUPER_SECRET" not in redacted
    assert "ABC123" not in redacted
    assert "<redacted:discord_bot_token>" in redacted
    assert "<redacted:password>" in redacted
    assert "<redacted:api_key>" in redacted

def test_redact_executor_text_private_key():
    raw = "BEGIN OPENSSH PRIVATE KEY\n12345\nEND OPENSSH PRIVATE KEY"
    redacted = redact_executor_text(raw)
    assert "12345" not in redacted
    assert "<redacted:private_key>" in redacted

def test_contains_secret_like_text():
    assert contains_secret_like_text("password=abc")
    assert not contains_secret_like_text("password_hash=abc") # wait, does "password=abc" match? Yes. What about "password_hash=abc"? It might match "password=" ? Let's check regex. The regex has `\b` or similar? No, it's `(?i)(password)=([^\s]+)`. So `password=abc` matches. `password_hash=abc` would not match because it's `password_hash`. But wait, `(password)=` would not match `password_hash=`. It requires exactly `password=`.

def test_redact_executor_data_recursive():
    raw_data = {
        "command_text": "DISCORD_BOT_TOKEN=12345",
        "nested": [
            {"api_key": "ABCDE"}
        ]
    }
    redacted = redact_executor_data(raw_data)
    assert redacted["command_text"] == "<redacted:discord_bot_token>"
    assert redacted["nested"][0]["api_key"] == "<redacted:api_key>"

