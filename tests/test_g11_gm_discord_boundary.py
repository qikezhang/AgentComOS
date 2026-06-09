import os
import subprocess
from pathlib import Path

def test_no_real_discord_connection_in_gm_discord():
    src_dir = Path("src/agentcomos/gm_discord")
    if not src_dir.exists():
        return
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()
        assert "discord.py" not in content
        assert "pycord" not in content
        assert "requests.post" not in content
        assert "aiohttp" not in content

def test_no_shell_execution_in_gm_discord():
    src_dir = Path("src/agentcomos/gm_discord")
    if not src_dir.exists():
        return
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()
        assert "subprocess" not in content
        assert "os.system" not in content

def test_no_unbounded_loops_in_gm_discord():
    src_dir = Path("src/agentcomos/gm_discord")
    if not src_dir.exists():
        return
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()
        assert "while True:" not in content
