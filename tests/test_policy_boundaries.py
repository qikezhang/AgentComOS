import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EX = ROOT / "examples/techai8/run/OI-TECHAI8-001"


def schema(name):
    return json.loads((SCHEMAS / name).read_text())


def validate(data, name):
    errors = list(Draft202012Validator(schema(name)).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_worker_invocation_boundary_positive():
    data = yaml.safe_load((EX / "worker_invocations/HWI-TF-001.yaml").read_text())
    validate(data, "worker_invocation.schema.json")
    assert data["created_by"] == "opencode"
    assert data["called_by"] == "opencode"
    assert data["gm_direct_access"] is False
    assert "DONE.md" in data["required_outputs"]
    assert {"call_gm", "call_user", "merge_git", "deploy"}.issubset(set(data["forbidden"]))


def test_worker_invocation_rejects_gm_creator():
    data = yaml.safe_load((EX / "worker_invocations/HWI-TF-001.yaml").read_text())
    data["created_by"] = "gm"
    errors = list(Draft202012Validator(schema("worker_invocation.schema.json")).iter_errors(data))
    assert errors


def test_industrial_auto_task_has_decision_and_feynman_artifacts():
    classification = yaml.safe_load((EX / "task_classification.yaml").read_text())
    assert classification["is_trivial"] is False
    assert classification["automation_stage"] == "industrial_auto"
    assert classification["decision_required"] is True
    assert classification["feynman_required"] is True
    for filename in ["decision_need_score.yaml", "decision_request.yaml", "final_decision.yaml", "feynman_result.yaml"]:
        assert (EX / filename).exists(), filename


def test_loop_batch_limits_workers_to_three():
    data = yaml.safe_load((EX / "loop_batch.yaml").read_text())
    validate(data, "loop_batch.schema.json")
    assert data["max_parallel_workers"] <= 3
    assert data["batch_stop_conditions"]


def test_runtime_context_requires_timezone_and_commands():
    data = yaml.safe_load((EX / "runtime_context_bundle.yaml").read_text())
    validate(data, "runtime_context_bundle.schema.json")
    assert data["timezone"]
    assert data["project_commands"]
