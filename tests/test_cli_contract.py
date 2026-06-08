import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=env)


def test_python_sources_compile():
    result = run([sys.executable, "-m", "compileall", "src", "tests"])
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_help_runs():
    result = run([sys.executable, "-m", "agentcomos.cli", "--help"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AgentComOS" in result.stdout


def test_validate_example_run():
    result = run([sys.executable, "-m", "agentcomos.cli", "validate", "examples/techai8/run/OI-TECHAI8-001"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Run validation passed" in result.stdout
