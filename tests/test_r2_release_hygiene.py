from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_env_example_no_secrets():
    content = (ROOT / ".env.example").read_text()
    assert "replace-with-deployment-secret" in content
    assert "DISCORD_BOT_TOKEN=" in content

def test_dockerignore_excludes_secrets():
    content = (ROOT / ".dockerignore").read_text()
    assert ".env" in content
    assert ".agentcomos/runs" in content
    assert "*.pem" in content or ".pem" in content

def test_r2_docs_exist():
    # Only verify the directory or basic known files exist to ensure we're testing on the right branch
    assert (ROOT / "docs" / "releases" / "v2.8").exists()
