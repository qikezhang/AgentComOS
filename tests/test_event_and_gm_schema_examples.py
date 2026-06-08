import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def validate(path, schema_name):
    data = yaml.safe_load(path.read_text())
    schema = json.loads((SCHEMAS / schema_name).read_text())
    errors = list(Draft202012Validator(schema).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_event_record_example_valid():
    validate(ROOT / "examples/observability/event_record.yaml", "event_record.schema.json")


def test_gm_message_example_valid():
    validate(ROOT / "examples/gm/gm_message_status_report.yaml", "gm_message.schema.json")
