from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_core_worker_registry_has_required_tiers():
    data = yaml.safe_load((ROOT / ".agentcomos/workers/registry/core_worker_registry.yaml").read_text())
    workers = {w["worker_id"]: w for w in data["workers"]}
    required = [
        "feynman_review_worker",
        "evidence_audit_worker",
        "risk_audit_worker",
        "release_judge_worker",
        "proposal_builder_worker",
        "proposal_scorer_worker",
        "critic_worker",
        "synthesis_worker",
        "final_decision_judge_worker",
    ]
    for worker_id in required:
        assert worker_id in workers


def test_worker_specs_forbid_gm_and_user():
    for path in (ROOT / ".agentcomos/workers/specs").glob("*.yaml"):
        spec = yaml.safe_load(path.read_text())
        assert spec["owner"] == "opencode"
        assert spec["runtime"] == "hermes_tmux"
        assert "opencode" in spec["allowed_called_by"]
        assert "gm" in spec["forbidden_called_by"]
        assert "user" in spec["forbidden_called_by"]
