from pathlib import Path
import json

import yaml
from jsonschema import Draft202012Validator

from agentcomos.worker.fake_hermes import write_fake_outputs
from agentcomos.worker.tmux_pool import build_fake_worker_shell_command


def write_invocation(tmp_path: Path, required_outputs: list[str] | None = None) -> Path:
    required_outputs = required_outputs or ["DONE.md", "result.yaml", "reasoning_summary.md"]
    output_dir = tmp_path / ".agentcomos" / "runs" / "OI-TECHAI8-001" / "worker_outputs" / "TF-001"
    invocation = {
        "invocation_id": "HWI-TF-001",
        "created_by": "opencode",
        "called_by": "opencode",
        "executed_by": "controller",
        "output_receiver": "opencode",
        "gm_direct_access": False,
        "worker_id": "seo_research_worker",
        "worker_version": "0.1.0",
        "runtime": "hermes_tmux",
        "task": {
            "task_id": "TF-001",
            "goal": "Validate fake worker.",
            "task_type": "research",
        },
        "inputs": ["task_contract.yaml"],
        "output_dir": str(output_dir),
        "required_outputs": required_outputs,
        "stop_conditions": ["required_outputs_exist"],
        "forbidden": ["call_gm", "call_user", "deploy", "merge_git", "real_hermes"],
    }
    path = tmp_path / "invocation.yaml"
    path.write_text(yaml.dump(invocation, sort_keys=False), encoding="utf-8")
    return path


def test_fake_hermes_worker_writes_done_result_summary(tmp_path):
    invocation = write_invocation(tmp_path)

    result = write_fake_outputs(invocation)

    output_dir = Path(result["output_dir"])
    assert (output_dir / "DONE.md").exists()
    assert (output_dir / "result.yaml").exists()
    assert (output_dir / "reasoning_summary.md").exists()
    done = (output_dir / "DONE.md").read_text(encoding="utf-8")
    result_yaml = yaml.safe_load((output_dir / "result.yaml").read_text(encoding="utf-8"))
    summary = (output_dir / "reasoning_summary.md").read_text(encoding="utf-8")
    assert "worker_runtime: fake_hermes" in done
    assert "real_hermes_used: false" in done
    assert result_yaml["worker_runtime"] == "fake_hermes"
    assert result_yaml["real_hermes_used"] is False
    assert "No real Hermes or LLM was used." in summary


def test_fake_hermes_worker_writes_additional_required_outputs(tmp_path):
    invocation = write_invocation(
        tmp_path,
        ["DONE.md", "result.yaml", "reasoning_summary.md", "unknown_facts.yaml", "failure_report.md"],
    )

    result = write_fake_outputs(invocation)

    output_dir = Path(result["output_dir"])
    assert (output_dir / "unknown_facts.yaml").exists()
    assert (output_dir / "failure_report.md").exists()


def test_worker_tmux_command_runs_fake_worker_only(tmp_path):
    invocation = write_invocation(tmp_path)
    command = build_fake_worker_shell_command(
        invocation=invocation,
        stdout_log=tmp_path / "stdout.log",
        stderr_log=tmp_path / "stderr.log",
        worktree=Path.cwd(),
    )

    assert "scripts/fake_hermes_worker.py" in command
    assert "hermes " not in command
    assert ("nous" + "research") not in command


def test_g4_worker_job_contract_matches_schema():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas" / "worker_job.schema.json").read_text(encoding="utf-8"))
    job = {
        "job_id": "HWJ-OI-TECHAI8-001-TF-001-001",
        "run_id": "OI-TECHAI8-001",
        "task_id": "TF-001",
        "invocation_id": "HWI-TF-001",
        "runtime": "tmux_fake_hermes",
        "status": "completed",
        "created_by": "controller",
        "started_by": "controller",
        "fake_worker": True,
        "real_hermes_used": False,
        "tmux_used": True,
        "tmux_session_name": "agentcomos-OI-TECHAI8-001-TF-001",
        "started_at": "2026-06-08T00:00:00+00:00",
        "completed_at": "2026-06-08T00:00:01+00:00",
        "output_dir": ".agentcomos/runs/OI-TECHAI8-001/worker_outputs/TF-001",
        "required_outputs": ["DONE.md", "result.yaml", "reasoning_summary.md"],
        "logs": {
            "stdout": "worker_logs/HWJ-OI-TECHAI8-001-TF-001-001.stdout.log",
            "stderr": "worker_logs/HWJ-OI-TECHAI8-001-TF-001-001.stderr.log",
        },
        "failure_reason": None,
    }
    errors = list(Draft202012Validator(schema).iter_errors(job))
    assert not errors, [error.message for error in errors]
