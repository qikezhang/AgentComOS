import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_dockerfile_exists():
    assert (ROOT / "Dockerfile").exists()

def test_docker_compose_exists():
    assert (ROOT / "docker-compose.yml").exists()

def test_env_example_exists():
    assert (ROOT / ".env.example").exists()

def test_dockerignore_exists():
    assert (ROOT / ".dockerignore").exists()

def test_docker_compose_valid():
    compose_path = ROOT / "docker-compose.yml"
    with open(compose_path, "r") as f:
        data = yaml.safe_load(f)
    
    assert "agentcomos" in data.get("services", {})
    service = data["services"]["agentcomos"]
    
    assert service.get("restart") == "unless-stopped"
    
    volumes = service.get("volumes", [])
    assert any(".agentcomos/runs:/app/.agentcomos/runs" in v for v in volumes)
    assert any("logs:/app/logs" in v for v in volumes)
    assert any("reports:/app/reports" in v for v in volumes)
    assert any("backups:/app/backups" in v for v in volumes)
    
    hc = service.get("healthcheck", {})
    assert "test" in hc
    assert "agentcomos" in hc["test"]
    assert "healthcheck" in hc["test"]
    
    assert not any("docker.sock" in v for v in volumes)
    assert not service.get("privileged", False)
