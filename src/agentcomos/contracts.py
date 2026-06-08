from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import re

import yaml
from jsonschema import Draft202012Validator


class ContractError(ValueError):
    """Raised when an AgentComOS cross-file contract is violated."""


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema(data: Any, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def expected_decision_mode(score: float) -> str:
    if score < 20:
        return "skip"
    if score < 50:
        return "mini"
    if score < 80:
        return "standard"
    return "full"


def worker_registry_ids(project_root: Path) -> set[str]:
    registry = project_root / ".agentcomos" / "workers" / "registry" / "core_worker_registry.yaml"
    data = load_yaml(registry)
    return {w["worker_id"] for w in data.get("workers", [])}


def validate_run_contract(run_dir: Path, project_root: Path | None = None) -> list[str]:
    """Validate AgentComOS cross-file contract for a run directory.

    中文备注：这里校验 schema 做不到的跨文件规则，例如 Decision Need Score 与 mode 是否一致、
    Worker Invocation 是否来自 OpenCode、Loop Batch 里的任务是否都有对应 invocation 等。
    """
    project_root = project_root or Path.cwd()
    errors: list[str] = []

    def y(name: str) -> Any:
        path = run_dir / name
        if not path.exists():
            errors.append(f"missing required run artifact: {name}")
            return None
        return load_yaml(path)

    classification = y("task_classification.yaml")
    dns = y("decision_need_score.yaml")
    feynman = y("feynman_result.yaml")
    loop_batch = y("loop_batch.yaml")
    batch_result = y("batch_result.yaml")
    final_decision = y("final_decision.yaml")

    if classification and dns:
        expected = expected_decision_mode(float(dns["score"]))
        if dns["mode"] != expected:
            errors.append(
                f"decision_need_score mode mismatch: score {dns['score']} expects {expected}, got {dns['mode']}"
            )

        stage = classification.get("automation_stage", "development_explicit")
        decision_trigger = classification.get("decision_trigger", "none")
        feynman_trigger = classification.get("feynman_trigger", "none")
        risk = classification.get("risk_level", "low")
        is_trivial = classification.get("is_trivial", False)

        # v2.8.5 stage policy:
        # - development_explicit: no system_auto for Decision/Feynman; user/task/high-risk only.
        # - transition_assisted: system may suggest, but not silently auto-enable.
        # - industrial_auto: policy can automatically require Decision/Feynman.
        if stage == "development_explicit":
            if classification.get("decision_required") and decision_trigger not in {"user_explicit", "task_policy", "forced_high_risk"}:
                errors.append("development_explicit stage requires explicit/task/forced trigger for Decision Market")
            if classification.get("feynman_required") and feynman_trigger not in {"user_explicit", "task_policy", "forced_high_risk"}:
                errors.append("development_explicit stage requires explicit/task/forced trigger for Feynman")

        if stage == "transition_assisted":
            if decision_trigger == "system_auto" or feynman_trigger == "system_auto":
                errors.append("transition_assisted stage must use gm_confirmed_system_suggestion, not silent system_auto")

        if stage == "industrial_auto":
            if not is_trivial and dns["mode"] != "skip" and not classification.get("decision_required"):
                errors.append("industrial_auto uncertain non-trivial task must require Decision Market")
            if not is_trivial and risk in {"medium", "high", "critical"} and not classification.get("feynman_required"):
                errors.append("industrial_auto medium/high/critical non-trivial task must require Feynman")
            if classification.get("decision_required") and decision_trigger not in {"system_auto", "user_explicit", "task_policy", "forced_high_risk", "gm_confirmed_system_suggestion"}:
                errors.append("industrial_auto decision_required requires a valid trigger")

        if risk in {"high", "critical"} and not classification.get("feynman_required"):
            errors.append("high/critical risk task must require Feynman or release gate")
        if classification.get("decision_required") and dns["mode"] == "skip":
            errors.append("decision_required=true cannot use decision mode skip")

    if feynman:
        vetoes = feynman.get("vetoes") or []
        if vetoes and feynman.get("decision") in {"accept", "accept_with_conditions"}:
            errors.append("feynman_result has vetoes but decision is accept/accept_with_conditions")
        if feynman.get("level") == "full":
            findings = " ".join(feynman.get("findings", []) + feynman.get("required_revisions", []))
            for term in ["security", "rollback", "manual"]:
                if term not in findings.lower():
                    errors.append(f"full feynman result must mention {term}")

    if final_decision:
        if final_decision.get("decision") in {"approved", "approved_with_conditions"} and final_decision.get("final_score", 0) < 75:
            errors.append("approved final decision must have final_score >= 75")
        if final_decision.get("decision") == "approved_with_conditions" and not final_decision.get("conditions"):
            errors.append("approved_with_conditions requires non-empty conditions")

    # Worker invocation contract.
    valid_worker_ids = worker_registry_ids(project_root)
    inv_dir = run_dir / "worker_invocations"
    invocations: dict[str, Any] = {}
    if inv_dir.exists():
        for path in inv_dir.glob("*.yaml"):
            data = load_yaml(path)
            invocations[data["task"]["task_id"]] = data
            worker_id = data.get("worker_id")
            if worker_id not in valid_worker_ids:
                errors.append(f"worker invocation {path.name} uses unknown worker_id: {worker_id}")
            required_forbidden = {"edit_project_files", "merge_git", "deploy", "call_gm", "call_user"}
            missing = required_forbidden - set(data.get("forbidden", []))
            if missing:
                errors.append(f"worker invocation {path.name} missing forbidden entries: {sorted(missing)}")
            if "DONE.md" not in data.get("required_outputs", []):
                errors.append(f"worker invocation {path.name} must require DONE.md")
            task_id = data["task"]["task_id"]
            output_dir = data.get("output_dir", "")
            pattern = rf"^\.agentcomos/runs/[^/]+/worker_outputs/{re.escape(task_id)}/$"
            if not re.match(pattern, output_dir):
                errors.append(
                    f"worker invocation {path.name} output_dir must be .agentcomos/runs/<run_id>/worker_outputs/{task_id}/"
                )
    else:
        errors.append("missing worker_invocations directory")

    if loop_batch:
        if loop_batch.get("max_parallel_workers", 0) > 3:
            errors.append("loop_batch max_parallel_workers cannot exceed 3")
        if loop_batch.get("max_tasks", 0) > 9:
            errors.append("loop_batch max_tasks cannot exceed 9")
        for task in loop_batch.get("tasks", []):
            task_id = task["task_id"]
            if task_id not in invocations:
                errors.append(f"loop task {task_id} has no matching Worker Invocation")
            else:
                inv_worker = invocations[task_id]["worker_id"]
                if inv_worker != task["worker_type"]:
                    errors.append(
                        f"loop task {task_id} worker_type {task['worker_type']} != invocation worker_id {inv_worker}"
                    )

    if loop_batch and batch_result:
        allowed = {task["task_id"] for task in loop_batch.get("tasks", [])}
        for key in ["completed_tasks", "failed_tasks", "blocked_tasks"]:
            for task_id in batch_result.get(key, []):
                if task_id not in allowed:
                    errors.append(f"batch_result {key} contains task not in loop_batch: {task_id}")

    # Release / versioning minimal contracts.
    change_set_path = run_dir / "change_set.yaml"
    rollback_path = run_dir / "rollback_target.yaml"
    if change_set_path.exists():
        change_set = load_yaml(change_set_path)
        risk = change_set.get("risk_level")
        if risk in {"medium", "high", "critical"} and not rollback_path.exists():
            errors.append("medium/high/critical change_set requires rollback_target.yaml")

    return errors


def assert_run_contract(run_dir: Path, project_root: Path | None = None) -> None:
    errors = validate_run_contract(run_dir, project_root)
    if errors:
        raise ContractError("\n".join(f"- {e}" for e in errors))
