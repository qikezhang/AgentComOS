import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EX = ROOT / "examples/techai8/run/OI-TECHAI8-001"

CASES = {
    "run_status.yaml": "run_status.schema.json",
    "opencode_job.yaml": "opencode_job.schema.json",
    "opencode_session_ledger.yaml": "opencode_session_ledger.schema.json",
    "worker_job.yaml": "worker_job.schema.json",
    "delivery_packet.yaml": "delivery_packet.schema.json",
    "proposal_card.yaml": "proposal_card.schema.json",
    "proposal_score.yaml": "proposal_score.schema.json",
    "critic_report.yaml": "critic_report.schema.json",
    "synthesized_plan.yaml": "synthesized_plan.schema.json",
    "final_decision.yaml": "final_decision.schema.json",
    "feynman_result.yaml": "feynman_result.schema.json",
    "loop_batch.yaml": "loop_batch.schema.json",
    "batch_result.yaml": "batch_result.schema.json",
    "manual_update_proposal.yaml": "manual_update_proposal.schema.json",
    "worker_evaluation.yaml": "worker_evaluation.schema.json",
    "failure_attribution.yaml": "failure_attribution.schema.json",
    "ratchet_decision.yaml": "ratchet_decision.schema.json",
    "change_set.yaml": "change_set.schema.json",
    "rollback_target.yaml": "rollback_target.schema.json",
}


def test_new_contract_examples_validate():
    for file_name, schema_name in CASES.items():
        data = yaml.safe_load((EX / file_name).read_text())
        schema = json.loads((SCHEMAS / schema_name).read_text())
        errors = list(Draft202012Validator(schema).iter_errors(data))
        assert not errors, f"{file_name} failed {schema_name}: {[e.message for e in errors]}"
