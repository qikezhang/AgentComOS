from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EX = ROOT / "examples" / "techai8" / "run" / "OI-TECHAI8-001"


def validate(path, schema):
    data = yaml.safe_load(path.read_text())
    schema_data = json.loads((SCHEMAS / schema).read_text())
    errors = list(Draft202012Validator(schema_data).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_operating_intent_example():
    validate(EX / "operating_intent.yaml", "operating_intent.schema.json")


def test_worker_invocation_boundary():
    validate(EX / "worker_invocations" / "HWI-TF-001.yaml", "worker_invocation.schema.json")
    data = yaml.safe_load((EX / "worker_invocations" / "HWI-TF-001.yaml").read_text())
    assert data["created_by"] == "opencode"
    assert data["called_by"] == "opencode"
    assert data["executed_by"] == "controller"
    assert data["gm_direct_access"] is False
    assert data["runtime"] == "hermes_tmux"


def test_decision_and_feynman_examples():
    validate(EX / "decision_request.yaml", "decision_request.schema.json")
    validate(EX / "feynman_check.yaml", "feynman_check.schema.json")


def test_loop_and_user_report_examples():
    validate(EX / "loop_execution_request.yaml", "loop_execution_request.schema.json")
    validate(EX / "user_report_packet.yaml", "user_report_packet.schema.json")
    validate(EX / "evidence_packet" / "manifest.yaml", "evidence_packet_manifest.schema.json")
