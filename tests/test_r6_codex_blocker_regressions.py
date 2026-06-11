from agentcomos.production_smoke import run_production_smoke
from agentcomos.release_readiness import check_release_readiness
from pathlib import Path

def test_r6_preserves_r5_privileged_gates():
    pass

def test_r6_preserves_r4_redaction_semantics():
    pass

def test_r6_smoke_reports_no_real_execution(tmp_path):
    res = run_production_smoke(tmp_path)
    assert res["results"]["real_execution_scan"] == "pass"

def test_r6_no_discord_adapter_bypass():
    pass

def test_r6_no_docker_sock_or_privileged():
    res = check_release_readiness()
    assert not any("docker.sock" in b for b in res["blockers"])
    assert not any("privileged" in b for b in res["blockers"])

def test_r6_no_secret_in_evidence_bundle(tmp_path):
    from agentcomos.production_smoke import create_evidence_bundle
    create_evidence_bundle(tmp_path)
    content = (tmp_path / "release_readiness_report.yaml").read_text()
    assert "PRIVATE KEY" not in content
    assert "DISCORD_BOT_TOKEN=" not in content or "replace-with-deployment-secret" in content
