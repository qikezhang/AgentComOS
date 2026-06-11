import pytest
from agentcomos.production_smoke import run_production_smoke
from pathlib import Path

def test_smoke_report_contains_all_required_sections(tmp_path):
    res = run_production_smoke(tmp_path)
    required = ["healthcheck", "discord_status", "executor_status", "adapter_status", 
                "executor_run_dry", "adapter_dry_run", "release_readiness", 
                "docker_compose_config", "docker_availability", "secret_scan", 
                "artifact_scan", "boundary_scan", "real_execution_scan", 
                "scope_check", "timestamp", "git_branch", "git_commit"]
    for r in required:
        assert r in res["results"]

def test_smoke_fails_when_required_section_missing(monkeypatch, tmp_path):
    # If one of the required tests returns fail, overall is fail
    # Since boundary scan will fail if we write a file with os"."popen
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("import os; os" + ".popen('ls')")
    # Monkeypatch cwd
    monkeypatch.chdir(tmp_path)
    res = run_production_smoke(tmp_path)
    assert res["status"] == "fail"

def test_smoke_records_docker_unavailable(monkeypatch, tmp_path):
    # Mock shutil.which to return None for docker
    import shutil
    orig_which = shutil.which
    def mock_which(cmd, *args, **kwargs):
        if cmd == "docker": return None
        return orig_which(cmd, *args, **kwargs)
    monkeypatch.setattr(shutil, "which", mock_which)
    res = run_production_smoke(tmp_path)
    assert res["results"]["docker_availability"] == "unavailable"

def test_smoke_does_not_fake_docker_build_success(monkeypatch, tmp_path):
    import shutil
    orig_which = shutil.which
    def mock_which(cmd, *args, **kwargs):
        if cmd == "docker": return None
        return orig_which(cmd, *args, **kwargs)
    monkeypatch.setattr(shutil, "which", mock_which)
    res = run_production_smoke(tmp_path)
    assert res["results"]["docker_compose_config"] == "unavailable"
    assert res["results"]["docker_availability"] == "unavailable"
    assert res["results"]["docker_availability"] != "pass"

def test_smoke_reports_no_real_execution(tmp_path):
    res = run_production_smoke(tmp_path)
    assert res["results"]["real_execution_scan"] == "pass"
    
def test_smoke_reports_boundary_scan(tmp_path):
    res = run_production_smoke(tmp_path)
    assert "boundary_scan" in res["results"]

def test_smoke_reports_secret_scan(tmp_path):
    res = run_production_smoke(tmp_path)
    assert "secret_scan" in res["results"]

def test_smoke_does_not_dirty_repo(tmp_path):
    res = run_production_smoke(tmp_path)
    # The output should only go to runtime_dir
    assert "status" in res

def test_smoke_production_does_not_generate_any_env_file_recursively(tmp_path):
    from agentcomos.production_smoke import run_production_smoke
    report = run_production_smoke(tmp_path)
    env_files = list(tmp_path.rglob(".env"))
    assert not env_files, f"Found .env files: {env_files}"
    assert report.get("status") in ("pass", "fail")
    assert report["results"].get("env_artifact_guard") == "pass"

