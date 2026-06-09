import json
import subprocess
import sys

def test_healthcheck_command():
    result = subprocess.run([sys.executable, "-m", "agentcomos.cli", "healthcheck"], capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert data["component"] == "agentcomos"
    assert data["mode"] == "healthcheck"
