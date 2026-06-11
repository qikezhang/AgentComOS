from agentcomos.production_smoke import run_production_smoke

def test_docker_smoke(tmp_path):
    res = run_production_smoke(tmp_path)
    assert "docker_compose_config" in res["results"]
