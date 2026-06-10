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

import subprocess
import shutil

def test_dockerfile_copies_src_before_project_install():
    dockerfile_path = ROOT / "Dockerfile"
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()
        
    pip_install_line = -1
    copy_src_line = -1
    
    for i, line in enumerate(lines):
        line_strip = line.strip()
        if ("pip install" in line_strip and "." in line_strip) and pip_install_line == -1:
            pip_install_line = i
        if (line_strip.startswith("COPY src") or line_strip.startswith("COPY ./src")) and copy_src_line == -1:
            copy_src_line = i
            
    assert pip_install_line != -1, "Could not find 'pip install .' in Dockerfile"
    assert copy_src_line != -1, "Could not find 'COPY src' in Dockerfile"
    assert copy_src_line < pip_install_line, "Dockerfile must COPY src before running pip install ."
    
    for line in lines:
        line_strip = line.strip()
        assert not line_strip.startswith("COPY .env"), "Dockerfile should not copy .env"
        assert not line_strip.startswith("COPY .agentcomos/runs"), "Dockerfile should not copy runs"

def test_docker_compose_config_uses_sanitized_temp_env(tmp_path):
    compose_src = ROOT / "docker-compose.yml"
    env_example = ROOT / ".env.example"
    
    compose_dst = tmp_path / "docker-compose.yml"
    env_dst = tmp_path / ".env"
    
    shutil.copy(compose_src, compose_dst)
    shutil.copy(env_example, env_dst)
    
    try:
        subprocess.run(["docker", "compose", "version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
        
    result = subprocess.run(["docker", "compose", "config"], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"docker compose config failed: {result.stderr}"
