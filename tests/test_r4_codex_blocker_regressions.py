import os
import pytest
from pathlib import Path
from typer.testing import CliRunner
from agentcomos.cli import app
from agentcomos.executor_request import ExecutorRequest
from agentcomos.executor_config import ExecutorConfig
from agentcomos.executor_framework import ExecutorFramework
from agentcomos.executor_policy import ExecutorPolicy

runner = CliRunner()

def test_executor_request_redacts_secret_before_artifact(tmp_path):
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env DISCORD_BOT_TOKEN=REAL_TOKEN_SHOULD_NOT_APPEAR",
        command_text="show env DISCORD_BOT_TOKEN=REAL_TOKEN_SHOULD_NOT_APPEAR",
        api_key="SUPER_SECRET_KEY"
    )
    artifact_path = tmp_path / "req.yaml"
    req.write_artifact(str(artifact_path))
    content = artifact_path.read_text()
    
    assert "REAL_TOKEN_SHOULD_NOT_APPEAR" not in content
    assert "SUPER_SECRET_KEY" not in content
    assert "<redacted:discord_bot_token>" in content
    assert "<redacted:api_key>" in content

def test_disabled_executor_deny_path_redacts_all_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env DISCORD_BOT_TOKEN=REAL_TOKEN_SHOULD_NOT_APPEAR"
    )
    config = ExecutorConfig()
    framework = ExecutorFramework(config, None)
    framework.process_request(req, str(tmp_path))
    
    for file in os.listdir(tmp_path):
        content = (tmp_path / file).read_text()
        assert "REAL_TOKEN_SHOULD_NOT_APPEAR" not in content

def test_missing_policy_deny_path_redacts_all_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env password=SUPER_SECRET_PASS"
    )
    config = ExecutorConfig()
    framework = ExecutorFramework(config, None)
    framework.process_request(req, str(tmp_path))
    
    for file in os.listdir(tmp_path):
        content = (tmp_path / file).read_text()
        assert "SUPER_SECRET_PASS" not in content

def test_run_dry_secret_request_redacts_result_and_audit(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env password=SUPER_SECRET_PASS"
    )
    config = ExecutorConfig()
    # Missing policy causes blocked decision
    framework = ExecutorFramework(config, None)
    decision, result = framework.process_request(req, str(tmp_path))
    
    result_content = (tmp_path / f"executor_result_{result.executor_result_id}.yaml").read_text()
    assert "SUPER_SECRET_PASS" not in result_content
    
    audit_content = (tmp_path / "executor_audit.yaml").read_text()
    assert "SUPER_SECRET_PASS" not in audit_content

def test_cli_evaluate_does_not_print_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    req_file = tmp_path / "req.yaml"
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env password=SUPER_SECRET_PASS"
    )
    req.write_artifact(str(req_file))
    
    result = runner.invoke(app, ["executor", "evaluate", "--request-file", str(req_file), "--runtime-dir", str(tmp_path)])
    assert "SUPER_SECRET_PASS" not in result.stdout

def test_cli_run_dry_does_not_print_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    req_file = tmp_path / "req.yaml"
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env password=SUPER_SECRET_PASS"
    )
    req.write_artifact(str(req_file))
    
    result = runner.invoke(app, ["executor", "run-dry", "--request-file", str(req_file), "--runtime-dir", str(tmp_path)])
    assert "SUPER_SECRET_PASS" not in result.stdout

def test_audit_markdown_never_contains_raw_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env api_key=ABC123456"
    )
    config = ExecutorConfig()
    framework = ExecutorFramework(config, None)
    framework.process_request(req, str(tmp_path))
    
    audit_file = tmp_path / "executor_audit.yaml"
    if audit_file.exists():
        assert "ABC123456" not in audit_file.read_text()

def test_redaction_recursive_for_nested_metadata():
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="",
        token="SECRET_TOKEN_XYZ",
        nested=[{"password": "SECRET_PASSWORD"}]
    )
    d = req.to_dict()
    assert d.get("token") == "<redacted:token>"
    assert d.get("nested")[0]["password"] == "<redacted:password>"

def test_secret_scan_generated_executor_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env api_key=ABC123456 token=XYZ789"
    )
    config = ExecutorConfig()
    framework = ExecutorFramework(config, None)
    framework.process_request(req, str(tmp_path))
    
    for file in os.listdir(tmp_path):
        content = (tmp_path / file).read_text()
        assert "ABC123456" not in content
        assert "XYZ789" not in content

def test_no_raw_command_text_field_in_executor_artifacts(tmp_path, monkeypatch):
    req = ExecutorRequest(
        source="cli",
        command_type="unknown",
        command_text_redacted="show env api_key=ABC123456 token=XYZ789",
        command_text="show env api_key=ABC123456 token=XYZ789"
    )
    req.write_artifact(str(tmp_path / "req.yaml"))
    
    content = (tmp_path / "req.yaml").read_text()
    assert "ABC123456" not in content
    assert "command_text_redacted:" in content

def test_blocked_secret_request_fixture_classifies_as_secret():
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    assert req.risk_level == "secret"
    assert req.reason == "secret_request_blocked"

def test_run_dry_blocked_secret_request_preserves_secret_semantics(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    policy = ExecutorPolicy({"version": 1})
    framework = ExecutorFramework(ExecutorConfig(), policy)
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    decision, result = framework.process_request(req, str(tmp_path))
    
    assert decision.risk_level == "secret"
    assert decision.reason == "secret_request_blocked"
    assert result.status == "blocked"
    
    audit_file = tmp_path / "executor_audit.yaml"
    assert "secret_request_blocked" in audit_file.read_text()
    assert "REAL_TOKEN" not in audit_file.read_text()

def test_evaluate_blocked_secret_request_preserves_secret_semantics(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    policy = ExecutorPolicy({"version": 1})
    framework = ExecutorFramework(ExecutorConfig(), policy)
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    decision = framework.evaluate(req)
    
    assert decision.risk_level == "secret"
    assert decision.reason == "secret_request_blocked"
    assert decision.decision == "blocked"

def test_redaction_masks_values_but_preserves_secret_keys():
    from agentcomos.executor_redaction import redact_executor_text
    input_text = "show env DISCORD_BOT_TOKEN=REAL_TOKEN password=SUPER_SECRET api_key=ABC123"
    output_text = redact_executor_text(input_text)
    assert "REAL_TOKEN" not in output_text
    assert "SUPER_SECRET" not in output_text
    assert "ABC123" not in output_text
    assert "<redacted:discord_bot_token>" in output_text
    assert "<redacted:password>" in output_text
    assert "<redacted:api_key>" in output_text

def test_policy_enabled_secret_request_does_not_become_unknown(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    policy = ExecutorPolicy({"version": 1})
    framework = ExecutorFramework(ExecutorConfig(), policy)
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    decision, result = framework.process_request(req, str(tmp_path))
    assert decision.risk_level == "secret"
    assert decision.reason == "secret_request_blocked"

def test_missing_policy_secret_request_keeps_secret_classification(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    framework = ExecutorFramework(ExecutorConfig(), None)
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    decision, result = framework.process_request(req, str(tmp_path))
    assert req.risk_level == "secret"
    assert req.reason == "secret_request_blocked"

def test_disabled_executor_secret_request_keeps_secret_classification(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "false")
    framework = ExecutorFramework(ExecutorConfig(), None)
    req = ExecutorRequest.load_artifact("tests/fixtures/executor/blocked_secret_request.yaml")
    decision, result = framework.process_request(req, str(tmp_path))
    assert req.risk_level == "secret"
    assert req.reason == "secret_request_blocked"

def test_cli_run_dry_secret_request_output_not_unknown_and_no_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    result = runner.invoke(app, ["executor", "run-dry", "--request-file", "tests/fixtures/executor/blocked_secret_request.yaml", "--runtime-dir", str(tmp_path)])
    assert "command_unknown" not in result.stdout
    assert "risk_level: unknown" not in result.stdout
    assert "REAL_TOKEN" not in result.stdout

def test_cli_evaluate_secret_request_output_not_unknown_and_no_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    result = runner.invoke(app, ["executor", "evaluate", "--request-file", "tests/fixtures/executor/blocked_secret_request.yaml", "--runtime-dir", str(tmp_path)])
    assert "command_unknown" not in result.stdout
    assert "risk_level: unknown" not in result.stdout
    assert "REAL_TOKEN" not in result.stdout

def test_codex_reproduction_secret_semantic(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROLLED_EXECUTOR_ENABLED", "true")
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text("version: 1\ndefault_decision: deny\nallow: []\nrequire_approval_for_high_risk: true")
    monkeypatch.setenv("CONTROLLED_EXECUTOR_POLICY_PATH", str(policy_path))
    result = runner.invoke(app, ["executor", "run-dry", "--request-file", "tests/fixtures/executor/blocked_secret_request.yaml", "--runtime-dir", str(tmp_path)])
    
    assert "command_unknown" not in result.stdout
    assert "REAL_TOKEN" not in result.stdout
    
    for file in os.listdir(tmp_path):
        content = (tmp_path / file).read_text()
        assert "REAL_TOKEN_SHOULD_NOT_APPEAR" not in content
        assert "command_unknown" not in content
        if "executor_decision" in file or "executor_audit" in file or "executor_request" in file:
            assert "secret_request_blocked" in content
            assert "secret" in content
