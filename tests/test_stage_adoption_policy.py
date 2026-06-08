from pathlib import Path
import yaml
import pytest

from agentcomos.contracts import assert_run_contract, ContractError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "techai8" / "run" / "OI-TECHAI8-001"


def test_development_explicit_example_can_disable_decision_and_feynman():
    data = yaml.safe_load((ROOT / "examples/policy/development-explicit-task-classification.yaml").read_text())
    assert data["automation_stage"] == "development_explicit"
    assert data["decision_required"] is False
    assert data["feynman_required"] is False
    assert data["decision_trigger"] == "none"


def test_industrial_auto_example_enables_system_auto():
    data = yaml.safe_load((ROOT / "examples/policy/industrial-auto-task-classification.yaml").read_text())
    assert data["automation_stage"] == "industrial_auto"
    assert data["decision_trigger"] == "system_auto"
    assert data["feynman_trigger"] == "system_auto"


def test_development_explicit_rejects_system_auto_trigger(tmp_path):
    import shutil
    run = tmp_path / "run"
    shutil.copytree(EXAMPLE, run)
    path = run / "task_classification.yaml"
    data = yaml.safe_load(path.read_text())
    data["automation_stage"] = "development_explicit"
    data["decision_required"] = True
    data["decision_trigger"] = "system_auto"
    data["feynman_required"] = True
    data["feynman_trigger"] = "system_auto"
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ContractError, match="development_explicit"):
        assert_run_contract(run, ROOT)


def test_industrial_auto_requires_decision_for_uncertain_task(tmp_path):
    import shutil
    run = tmp_path / "run"
    shutil.copytree(EXAMPLE, run)
    path = run / "task_classification.yaml"
    data = yaml.safe_load(path.read_text())
    data["automation_stage"] = "industrial_auto"
    data["decision_required"] = False
    data["decision_trigger"] = "none"
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ContractError, match="industrial_auto"):
        assert_run_contract(run, ROOT)
