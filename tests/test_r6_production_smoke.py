from agentcomos.production_smoke import run_production_smoke
from pathlib import Path

def test_production_smoke(tmp_path):
    res = run_production_smoke(tmp_path)
    assert res["status"] in ["pass", "fail", "warn"]
    assert "healthcheck" in res["results"]
