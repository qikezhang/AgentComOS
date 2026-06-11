from agentcomos.production_smoke import run_production_smoke

def test_docker_smoke(tmp_path):
    res = run_production_smoke(tmp_path)
    assert "docker_compose_config" in res["results"]

def test_compose_clean_workspace_is_outside_runtime_dir(tmp_path):
    from agentcomos.production_smoke import run_production_smoke
    report = run_production_smoke(tmp_path)
    compose_dir = tmp_path / "compose_clean"
    assert not compose_dir.exists(), "compose_clean should not exist in runtime_dir"
    dc_summary = report["results"].get("docker_compose_config_summary", {})
    if dc_summary.get("status") != "unavailable":
        assert dc_summary.get("persisted_env_file") is False
        assert dc_summary.get("temp_workspace_used") is True

def test_fresh_docker_unavailable_not_old_image_evidence(tmp_path):
    from agentcomos.production_smoke import run_production_smoke
    import shutil
    if not shutil.which("docker"):
        report = run_production_smoke(tmp_path)
        assert report["results"]["docker_availability"] == "unavailable"

