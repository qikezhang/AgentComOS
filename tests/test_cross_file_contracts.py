from pathlib import Path
import shutil
import yaml

import pytest

from agentcomos.contracts import assert_run_contract, ContractError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "techai8" / "run" / "OI-TECHAI8-001"


def copy_run(tmp_path: Path) -> Path:
    target = tmp_path / "run"
    shutil.copytree(EXAMPLE, target)
    return target


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def test_valid_example_cross_file_contract():
    assert_run_contract(EXAMPLE, ROOT)


def test_decision_score_mode_mismatch_fails(tmp_path):
    run = copy_run(tmp_path)
    path = run / "decision_need_score.yaml"
    data = yaml.safe_load(path.read_text())
    data["score"] = 85
    data["mode"] = "mini"
    write_yaml(path, data)
    with pytest.raises(ContractError, match="mode mismatch"):
        assert_run_contract(run, ROOT)


def test_development_explicit_can_skip_when_not_requested(tmp_path):
    run = copy_run(tmp_path)
    cls_path = run / "task_classification.yaml"
    cls = yaml.safe_load(cls_path.read_text())
    cls.update({
        "automation_stage": "development_explicit",
        "decision_required": False,
        "feynman_required": False,
        "decision_trigger": "none",
        "feynman_trigger": "none",
    })
    write_yaml(cls_path, cls)
    dns_path = run / "decision_need_score.yaml"
    dns = yaml.safe_load(dns_path.read_text())
    dns["score"] = 10
    dns["mode"] = "skip"
    write_yaml(dns_path, dns)
    assert_run_contract(run, ROOT)


def test_worker_id_must_exist_in_registry(tmp_path):
    run = copy_run(tmp_path)
    path = run / "worker_invocations" / "HWI-TF-001.yaml"
    data = yaml.safe_load(path.read_text())
    data["worker_id"] = "not_a_real_worker"
    write_yaml(path, data)
    with pytest.raises(ContractError, match="unknown worker_id"):
        assert_run_contract(run, ROOT)


def test_worker_output_dir_must_match_task_id(tmp_path):
    run = copy_run(tmp_path)
    path = run / "worker_invocations" / "HWI-TF-001.yaml"
    data = yaml.safe_load(path.read_text())
    data["output_dir"] = ".agentcomos/runs/OI-TECHAI8-001/worker_outputs/WRONG/"
    write_yaml(path, data)
    with pytest.raises(ContractError, match="output_dir"):
        assert_run_contract(run, ROOT)


def test_loop_task_requires_matching_invocation(tmp_path):
    run = copy_run(tmp_path)
    (run / "worker_invocations" / "HWI-TF-002.yaml").unlink()
    with pytest.raises(ContractError, match="TF-002"):
        assert_run_contract(run, ROOT)


def test_feynman_veto_blocks_accept(tmp_path):
    run = copy_run(tmp_path)
    path = run / "feynman_result.yaml"
    data = yaml.safe_load(path.read_text())
    data["decision"] = "accept"
    data["vetoes"] = ["missing_required_output"]
    write_yaml(path, data)
    with pytest.raises(ContractError, match="vetoes"):
        assert_run_contract(run, ROOT)
