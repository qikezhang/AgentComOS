from __future__ import annotations

from pathlib import Path
import json
import shlex
import shutil
from typing import Any

import typer
import yaml
from jsonschema import Draft202012Validator
from rich import print

from agentcomos.contracts import assert_run_contract, ContractError

app = typer.Typer(help="AgentComOS controller CLI skeleton")
ROOT = Path.cwd()
SCHEMAS = ROOT / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS / name
    if not path.exists():
        raise typer.BadParameter(f"schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_file(path: Path, schema_name: str) -> Any:
    if not path.exists():
        raise typer.BadParameter(f"file does not exist: {path}")
    schema = load_schema(schema_name)
    data = load_yaml(path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        details = "\n".join(
            f"- {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
        )
        raise typer.BadParameter(f"{path} failed {schema_name}:\n{details}")
    return data


def q(value: Path | str) -> str:
    return shlex.quote(str(value))


@app.command()
def doctor() -> None:
    """Check local developer tools."""
    tools = ["git", "docker", "tmux", "opencode", "hermes"]
    for tool in tools:
        found = shutil.which(tool)
        color = "green" if found else "yellow"
        print(f"[{color}]{tool}:[/] {found or 'not found'}")
    print("[bold]Note:[/] missing opencode/hermes is acceptable before runtime integration; schemas/tests still run.")


@app.command()
def validate(run_dir: Path) -> None:
    """Validate an example run directory."""
    if not run_dir.exists():
        raise typer.BadParameter(f"run dir does not exist: {run_dir}")
    checks = [
        (run_dir / "operating_intent.yaml", "operating_intent.schema.json"),
        (run_dir / "task_classification.yaml", "task_classification.schema.json"),
        (run_dir / "decision_need_score.yaml", "decision_need_score.schema.json"),
        (run_dir / "decision_request.yaml", "decision_request.schema.json"),
        (run_dir / "proposal_card.yaml", "proposal_card.schema.json"),
        (run_dir / "proposal_score.yaml", "proposal_score.schema.json"),
        (run_dir / "critic_report.yaml", "critic_report.schema.json"),
        (run_dir / "synthesized_plan.yaml", "synthesized_plan.schema.json"),
        (run_dir / "final_decision.yaml", "final_decision.schema.json"),
        (run_dir / "feynman_check.yaml", "feynman_check.schema.json"),
        (run_dir / "feynman_result.yaml", "feynman_result.schema.json"),
        (run_dir / "loop_execution_request.yaml", "loop_execution_request.schema.json"),
        (run_dir / "loop_batch.yaml", "loop_batch.schema.json"),
        (run_dir / "batch_result.yaml", "batch_result.schema.json"),
        (run_dir / "next_frontier_candidates.yaml", "next_frontier_candidates.schema.json"),
        (run_dir / "worker_invocations" / "HWI-TF-001.yaml", "worker_invocation.schema.json"),
        (run_dir / "worker_job.yaml", "worker_job.schema.json"),
        (run_dir / "opencode_job.yaml", "opencode_job.schema.json"),
        (run_dir / "opencode_session_ledger.yaml", "opencode_session_ledger.schema.json"),
        (run_dir / "run_status.yaml", "run_status.schema.json"),
        (run_dir / "delivery_packet.yaml", "delivery_packet.schema.json"),
        (run_dir / "user_report_packet.yaml", "user_report_packet.schema.json"),
        (run_dir / "runtime_context_bundle.yaml", "runtime_context_bundle.schema.json"),
        (run_dir / "evidence_packet" / "manifest.yaml", "evidence_packet_manifest.schema.json"),
    ]
    for path, schema_name in checks:
        validate_file(path, schema_name)
        print(f"[green]OK[/] {path.relative_to(run_dir)} -> {schema_name}")
    try:
        assert_run_contract(run_dir, ROOT)
    except ContractError as exc:
        raise typer.BadParameter(f"cross-file contract failed:\n{exc}") from exc
    print("[bold green]Run validation passed[/]")


@app.command("build-worker-command")
def build_worker_command(invocation: Path, session: str = typer.Option(...), worktree: Path = typer.Option(Path("."))) -> None:
    """Print the tmux + Hermes CLI command for a Worker Invocation."""
    data = validate_file(invocation, "worker_invocation.schema.json")
    output_dir = data["output_dir"]
    prompt = f"Read {invocation} and write all required outputs to {output_dir}/"
    command = (
        "tmux new-session -d "
        f"-s {q(session)} "
        f"\"cd {q(worktree)} && hermes chat -Q -q {q(prompt)}\""
    )
    print(command)


@app.command("opencode-command")
def opencode_command(run_id: str, phase: str = "plan", server: str = "http://127.0.0.1:4096") -> None:
    """Print a safe OpenCode attach command skeleton."""
    title = f"{run_id} {phase}"
    cmd = [
        "opencode", "run", "--attach", server,
        "--agent", f"agentcomos-{phase}",
        "--dir", f".worktrees/{run_id}/opencode",
        "--title", title,
        "--format", "json",
        f"Read .agentcomos/runs/{run_id}/operating_intent.yaml and runtime_context_bundle.yaml. Execute .opencode/commands/accept-gm-intent.md.",
    ]
    print(" ".join(q(part) for part in cmd))


run_app = typer.Typer(help="Manage runs")
app.add_typer(run_app, name="run")

controller_app = typer.Typer(help="Controller operations")
app.add_typer(controller_app, name="controller")

@run_app.command("create")
def run_create(intent: Path = typer.Option(..., help="Path to operating_intent.yaml")) -> None:
    """Create a new run from an operating intent."""
    from agentcomos.controller.runner import handle_run_create
    try:
        handle_run_create(intent)
    except ValueError as e:
        raise typer.BadParameter(str(e))

@run_app.command("status")
def run_status(run: str = typer.Option(..., help="Run ID")) -> None:
    """Show the status of a run."""
    from agentcomos.controller.runner import handle_run_status
    handle_run_status(run)

@controller_app.command("tick")
def controller_tick(run: str = typer.Option(..., help="Run ID"), fake: bool = typer.Option(False, "--fake", help="Fake execution")) -> None:
    """Advance the state machine for a run."""
    from agentcomos.controller.runner import handle_controller_tick
    try:
        handle_controller_tick(run, fake)
    except ValueError as e:
        raise typer.BadParameter(str(e))

@controller_app.command("recover")
def controller_recover(run: str = typer.Option(..., help="Run ID")) -> None:
    """Recover a run from its event log."""
    from agentcomos.controller.runner import handle_controller_recover
    try:
        handle_controller_recover(run)
    except ValueError as e:
        raise typer.BadParameter(str(e))


if __name__ == "__main__":
    app()
