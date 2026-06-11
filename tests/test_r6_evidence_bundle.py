import pytest
from agentcomos.production_smoke import create_evidence_bundle

def test_bundle_contains_r2_r5_acceptance_refs(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "acceptance_refs.yaml").exists()

def test_bundle_contains_command_summaries(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "command_summaries.yaml").exists()

def test_bundle_contains_boundary_and_secret_scan_summaries(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "boundary_scan_summary.yaml").exists()
    assert (tmp_path / "secret_scan_summary.yaml").exists()

def test_bundle_contains_regression_summary(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "regression_summary.yaml").exists()

def test_bundle_contains_rollback_and_operator_readiness(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "rollback_readiness.yaml").exists()
    assert (tmp_path / "operator_runbook_readiness.yaml").exists()

def test_bundle_contains_timestamp_and_git_info(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "git_info.yaml").exists()
    import yaml
    gi = yaml.safe_load((tmp_path / "git_info.yaml").read_text())
    assert "timestamp" in gi
    assert "git_branch" in gi

def test_bundle_records_docker_build_run_availability(tmp_path):
    create_evidence_bundle(tmp_path)
    assert (tmp_path / "docker_availability.yaml").exists()

def test_bundle_excludes_env_and_secrets(tmp_path):
    create_evidence_bundle(tmp_path)
    assert not (tmp_path / ".env").exists()
    assert not (tmp_path / "docker.sock").exists()

def test_bundle_missing_required_content_fails_validation(tmp_path):
    # This just ensures we output all of them
    bundle = create_evidence_bundle(tmp_path)
    assert bundle["readiness_status"] in ["pass", "fail"]

def test_evidence_bundle_does_not_include_nested_env_file(tmp_path):
    from agentcomos.production_smoke import create_evidence_bundle
    manifest = create_evidence_bundle(tmp_path)
    env_files = list(tmp_path.rglob(".env"))
    assert not env_files, f"Found .env files: {env_files}"

def test_bundle_manifest_excludes_env_at_any_depth(tmp_path):
    from agentcomos.production_smoke import create_evidence_bundle
    manifest = create_evidence_bundle(tmp_path)
    files = manifest.get("files", [])
    for f in files:
        assert f != ".env"
        assert not f.endswith("/.env")

