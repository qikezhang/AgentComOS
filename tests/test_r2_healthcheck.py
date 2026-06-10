import json
import subprocess
import sys
import os
from pathlib import Path

def test_healthcheck_command(tmp_path):
    root = Path(__file__).parent.parent
    runs_dir = root / ".agentcomos" / "runs"
    
    # Store initial state of runs_dir
    runs_existed = runs_dir.exists()
    
    # Ensure healthcheck can run with tmp_path if needed, or check it doesn't create root dirs
    env = os.environ.copy()
    
    result = subprocess.run(
        [sys.executable, "-m", "agentcomos.cli", "healthcheck"], 
        capture_output=True, 
        text=True,
        env=env
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert data["component"] == "agentcomos"
    assert data["mode"] == "healthcheck"
    
    # Hygiene: healthcheck does not create .agentcomos/runs if it was missing
    if not runs_existed:
        assert not runs_dir.exists(), "healthcheck should not create .agentcomos/runs if missing"

