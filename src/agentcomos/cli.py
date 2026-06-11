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
    """Print the G4 tmux fake Hermes worker command for a Worker Invocation."""
    data = validate_file(invocation, "worker_invocation.schema.json")
    from agentcomos.worker.tmux_pool import build_fake_worker_shell_command

    job_id = f"HWI-COMMAND-{data['task']['task_id']}"
    stdout_log = Path(data["output_dir"]) / f"{job_id}.stdout.log"
    stderr_log = Path(data["output_dir"]) / f"{job_id}.stderr.log"
    shell_command = build_fake_worker_shell_command(
        invocation=invocation,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=worktree,
    )
    print(f"tmux new-session -d -s {q(session)} {q(shell_command)}")


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

loop_app = typer.Typer(help="Loop Execution operations")
app.add_typer(loop_app, name="loop")

opencode_app = typer.Typer(help="OpenCode runtime operations")
app.add_typer(opencode_app, name="opencode")

worker_app = typer.Typer(help="Worker runtime operations")
app.add_typer(worker_app, name="worker")

program_app = typer.Typer(help="Operating Program operations")
app.add_typer(program_app, name="program")

frontier_app = typer.Typer(help="Task Frontier operations")
app.add_typer(frontier_app, name="frontier")

decision_app = typer.Typer(help="Decision operations")
app.add_typer(decision_app, name="decision")

feynman_app = typer.Typer(help="Feynman operations")
app.add_typer(feynman_app, name="feynman")

manual_os_app = typer.Typer(help="Manual OS Controlled Adoption operations")
app.add_typer(manual_os_app, name="manual-os")

gm_discord_app = typer.Typer(help="GM Discord Controlled Bridge operations")
app.add_typer(gm_discord_app, name="gm-discord")

discord_app = typer.Typer(help="Real Discord Bot Adapter operations")
app.add_typer(discord_app, name="discord")

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
    try:
        handle_run_status(run)
    except ValueError as e:
        raise typer.BadParameter(str(e))

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


@loop_app.command("plan")
def loop_plan_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Create a loop plan."""
    from agentcomos.loop.plan import create_loop_plan
    import yaml
    try:
        plan = create_loop_plan(run)
        print(yaml.dump(plan, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@loop_app.command("status")
def loop_status_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Show the status of a loop."""
    from agentcomos.loop.status import get_loop_status
    import yaml
    try:
        status = get_loop_status(run)
        print(yaml.dump(status, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@loop_app.command("run")
def loop_run_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    max_ticks: int = typer.Option(..., "--max-ticks", help="Maximum number of ticks to run"),
    fake: bool = typer.Option(False, "--fake", help="Fake execution")
) -> None:
    """Execute loop runner."""
    from agentcomos.loop.runner import run_loop
    try:
        run_loop(run, max_ticks, fake)
    except ValueError as e:
        raise typer.BadParameter(str(e))

@loop_app.command("trace")
def loop_trace_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Show the trace of a loop."""
    from agentcomos.loop.trace import read_loop_trace
    import yaml
    try:
        trace = read_loop_trace(run)
        print(yaml.dump(trace, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@loop_app.command("recover")
def loop_recover_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Recover the status of a loop from trace."""
    from agentcomos.loop.recover import recover_loop_status
    import yaml
    try:
        status = recover_loop_status(run)
        print("Loop recovered successfully:")
        print(yaml.dump(status, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@program_app.command("build")
def program_build(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Build operating_program.yaml for a run."""
    from agentcomos.program.builder import build_operating_program
    try:
        program = build_operating_program(run)
        print(yaml.dump(program, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@program_app.command("status")
def program_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Show Operating Program status."""
    from agentcomos.program.status import get_program_status
    try:
        print(yaml.dump(get_program_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@frontier_app.command("build")
def frontier_build(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Build task_frontier.yaml for a run."""
    from agentcomos.frontier.builder import build_task_frontier
    from agentcomos.frontier.status import generate_frontier_status
    try:
        frontier = build_task_frontier(run)
        generate_frontier_status(run)
        print(yaml.dump(frontier, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@frontier_app.command("status")
def frontier_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Show Task Frontier status."""
    from agentcomos.frontier.status import generate_frontier_status
    try:
        print(yaml.dump(generate_frontier_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@frontier_app.command("list")
def frontier_list(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """List Task Frontier items."""
    from agentcomos.frontier.status import list_frontier_tasks
    try:
        print(yaml.dump(list_frontier_tasks(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@frontier_app.command("next")
def frontier_next(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Show the next ready Task Frontier item."""
    from agentcomos.frontier.builder import read_task_frontier
    from agentcomos.frontier.scheduler import next_ready_task
    from agentcomos.program.builder import validate_run_exists
    try:
        validate_run_exists(run)
        frontier = read_task_frontier(run)
        task = next_ready_task(frontier) if frontier else None
        print(yaml.dump({"run_id": run, "next_task": task}, sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))


@frontier_app.command("update")
def frontier_update(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    status: str = typer.Option(..., "--status", help="Task status"),
) -> None:
    """Update a Task Frontier item status."""
    from agentcomos.frontier.executor import update_task_status
    try:
        print(yaml.dump(update_task_status(run, task, status), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@opencode_app.command("submit")
def opencode_submit(
    run: str = typer.Option(..., help="Run ID"),
    fake: bool = typer.Option(False, "--fake", help="Fake execution"),
    real: bool = typer.Option(False, "--real", help="Real execution"),
    phase: str = typer.Option("plan", "--phase", help="Phase to execute")
) -> None:
    """Submit an OpenCode job."""
    if real:
        from agentcomos.opencode.real_runtime import submit_real_job
        try:
            job_id = submit_real_job(run, phase=phase)
            print(f"Real job submitted: {job_id}")
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif fake:
        from agentcomos.opencode.fake_runtime import submit_fake_job
        try:
            job_id = submit_fake_job(run)
            print(f"Fake job submitted: {job_id}")
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter("Must specify either --fake or --real")

@opencode_app.command("status")
def opencode_status(job: str | None = typer.Option(None, help="Job ID")) -> None:
    """Check the status of an OpenCode job or check runtime availability."""
    if job is None:
        from agentcomos.opencode.availability import check_opencode_availability
        from rich import print
        status = check_opencode_availability()
        print(status)
        return

    from agentcomos.opencode.jobs import read_job, detect_job_runtime
    parts = job.split("-")
    if len(parts) >= 3:
        run_id = "-".join(parts[1:-1])
    else:
        raise typer.BadParameter("Invalid job ID format. Expected OCJ-<run_id>-<retry>")
    
    job_data = read_job(run_id, job)
    if not job_data:
        raise typer.BadParameter(f"Job not found: {job}")
        
    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.opencode.real_runtime import status_real_job
        try:
            status_real_job(run_id, job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        from agentcomos.opencode.fake_runtime import status_fake_job
        try:
            status_fake_job(run_id, job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for job {job}")

@opencode_app.command("collect")
def opencode_collect(job: str = typer.Option(..., help="Job ID")) -> None:
    """Collect completed OpenCode job outputs."""
    from agentcomos.opencode.jobs import read_job, detect_job_runtime
    parts = job.split("-")
    if len(parts) >= 3:
        run_id = "-".join(parts[1:-1])
    else:
        raise typer.BadParameter("Invalid job ID format. Expected OCJ-<run_id>-<retry>")
    
    job_data = read_job(run_id, job)
    if not job_data:
        raise typer.BadParameter(f"Job not found: {job}")
        
    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.opencode.real_runtime import collect_real_job
        try:
            collect_real_job(run_id, job)
            print(f"Real job collected or in read-only mode: {job}")
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        from agentcomos.opencode.fake_runtime import collect_fake_job
        try:
            collect_fake_job(run_id, job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for job {job}")

@opencode_app.command("recover")
def opencode_recover(job: str = typer.Option(..., help="Job ID")) -> None:
    """Recover an OpenCode job."""
    from agentcomos.opencode.jobs import read_job, detect_job_runtime
    parts = job.split("-")
    if len(parts) >= 3:
        run_id = "-".join(parts[1:-1])
    else:
        raise typer.BadParameter("Invalid job ID format. Expected OCJ-<run_id>-<retry>")
    
    job_data = read_job(run_id, job)
    if not job_data:
        raise typer.BadParameter(f"Job not found: {job}")
        
    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.opencode.real_runtime import recover_real_job
        try:
            recover_real_job(run_id, job)
            print(f"Real job recovered: {job}")
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        raise typer.BadParameter("Fake recover not implemented or required")
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for job {job}")


@opencode_app.command("start")
@opencode_app.command("serve")
def opencode_start() -> None:
    """Construct and show the OpenCode serve command."""
    from agentcomos.opencode.commands import build_opencode_serve_command
    from rich import print
    print(build_opencode_serve_command())


@worker_app.command("hermes-status")
def worker_hermes_status() -> None:
    """Check Hermes CLI availability and write status artifact."""
    from agentcomos.worker.availability import check_hermes_availability
    from rich import print
    status = check_hermes_availability()
    print(status)


@worker_app.command("start")
def worker_start(
    invocation: Path = typer.Option(..., "--invocation", help="Path to worker_invocation.yaml"),
    fake: bool = typer.Option(False, "--fake", help="Run fake Hermes worker in tmux"),
    real: bool = typer.Option(False, "--real", help="Run real Hermes worker in tmux"),
) -> None:
    """Start a worker job from a Worker Invocation."""
    if real:
        from agentcomos.worker.real_runtime import start_real_worker
        try:
            start_real_worker(invocation)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif fake:
        from agentcomos.worker.fake_runtime import start_fake_worker
        try:
            start_fake_worker(invocation, fake=fake)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter("Must specify either --fake or --real")


@worker_app.command("status")
def worker_status(job: str = typer.Option(..., "--job", help="Worker job ID")) -> None:
    """Read worker job status without mutating artifacts."""
    from agentcomos.worker.jobs import find_worker_job, detect_job_runtime

    found = find_worker_job(job)
    if not found:
        raise typer.BadParameter(f"Worker job not found: {job}")
    _, job_data = found

    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.worker.real_runtime import status_real_worker
        try:
            status_real_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        from agentcomos.worker.fake_runtime import status_fake_worker
        try:
            status_fake_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for worker job {job}")


@worker_app.command("collect")
def worker_collect(job: str = typer.Option(..., "--job", help="Worker job ID")) -> None:
    """Collect worker outputs and update job status when complete."""
    from agentcomos.worker.jobs import find_worker_job, detect_job_runtime

    found = find_worker_job(job)
    if not found:
        raise typer.BadParameter(f"Worker job not found: {job}")
    _, job_data = found

    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.worker.real_runtime import collect_real_worker
        try:
            collect_real_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        from agentcomos.worker.fake_runtime import collect_fake_worker
        try:
            collect_fake_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for worker job {job}")


@worker_app.command("kill")
def worker_kill(job: str = typer.Option(..., "--job", help="Worker job ID")) -> None:
    """Kill a worker tmux session when available."""
    from agentcomos.worker.jobs import find_worker_job, detect_job_runtime

    found = find_worker_job(job)
    if not found:
        raise typer.BadParameter(f"Worker job not found: {job}")
    _, job_data = found

    runtime_type = detect_job_runtime(job_data)
    if runtime_type == "real":
        from agentcomos.worker.real_runtime import kill_real_worker
        try:
            kill_real_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    elif runtime_type == "fake":
        from agentcomos.worker.fake_runtime import kill_fake_worker
        try:
            kill_fake_worker(job)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    else:
        raise typer.BadParameter(f"Cannot determine runtime type for worker job {job}")


@worker_app.command("list")
def worker_list(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """List worker jobs for a run."""
    from agentcomos.worker.fake_runtime import list_fake_workers

    try:
        list_fake_workers(run)
    except ValueError as e:
        raise typer.BadParameter(str(e))


@worker_app.command("recover")
def worker_recover(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    """Recover worker jobs for a run from existing artifacts."""
    from agentcomos.worker.fake_runtime import recover_fake_workers
    from agentcomos.worker.real_runtime import recover_real_workers
    try:
        recover_fake_workers(run)
        recover_real_workers(run)
    except ValueError as e:
        raise typer.BadParameter(str(e))




evidence_app = typer.Typer(help="Evidence operations")
app.add_typer(evidence_app, name="evidence")

delivery_app = typer.Typer(help="Delivery operations")
app.add_typer(delivery_app, name="delivery")

gm_app = typer.Typer(help="GM operations")
app.add_typer(gm_app, name="gm")

@evidence_app.command("build")
def evidence_build(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.evidence.builder import build_evidence_packet
    try:
        build_evidence_packet(run)
        print("Evidence built.")
    except Exception as e:
        raise typer.BadParameter(str(e))

@evidence_app.command("status")
def evidence_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.evidence.builder import get_evidence_status
    print(get_evidence_status(run))

@delivery_app.command("build")
def delivery_build(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.delivery.builder import build_delivery_packet
    try:
        build_delivery_packet(run)
        print("Delivery built.")
    except Exception as e:
        raise typer.BadParameter(str(e))

@delivery_app.command("status")
def delivery_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.delivery.builder import get_delivery_status
    print(get_delivery_status(run))

@gm_app.command("report")
def gm_report_cmd(run: str = typer.Option(..., "--run", help="Run ID"), format: str = typer.Option("markdown", "--format", help="Format: markdown or yaml")) -> None:
    from agentcomos.gm.report import generate_gm_report
    try:
        generate_gm_report(run, format=format)
        print("GM report generated.")
    except Exception as e:
        raise typer.BadParameter(str(e))

@decision_app.command("request")
def decision_request(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    mode: str = typer.Option(None, "--mode", help="Mode (must be explicit)")
) -> None:
    if mode != "explicit":
        raise typer.BadParameter("mode must be 'explicit'")
    from agentcomos.decision.builder import request_decision
    try:
        request_decision(run, task, mode)
        print("Decision requested and deterministic result generated.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@decision_app.command("status")
def decision_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.decision.status import get_decision_status
    import yaml
    try:
        print(yaml.dump(get_decision_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@decision_app.command("result")
def decision_result(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID")
) -> None:
    from agentcomos.decision.status import get_decision_result
    import yaml
    try:
        print(yaml.dump(get_decision_result(run, task), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@feynman_app.command("check")
def feynman_check_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    mode: str = typer.Option(None, "--mode", help="Mode (must be explicit)")
) -> None:
    if mode != "explicit":
        raise typer.BadParameter("mode must be 'explicit'")
    from agentcomos.feynman.builder import check_feynman
    try:
        check_feynman(run, task, mode)
        print("Feynman check requested and deterministic result generated.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@feynman_app.command("status")
def feynman_status_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.feynman.status import get_feynman_status
    import yaml
    try:
        print(yaml.dump(get_feynman_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@feynman_app.command("result")
def feynman_result_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID")
) -> None:
    from agentcomos.feynman.status import get_feynman_result
    import yaml
    try:
        print(yaml.dump(get_feynman_result(run, task), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))
@manual_os_app.command("request")
def manual_os_request_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID")
) -> None:
    from agentcomos.manual_os.request import create_request
    try:
        req = create_request(run, task)
        print(f"Manual OS request created for {task} in {run}.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@manual_os_app.command("status")
def manual_os_status_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.manual_os.status import get_manual_os_status
    import yaml
    try:
        print(yaml.dump(get_manual_os_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@manual_os_app.command("approve")
def manual_os_approve_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    approved_by: str = typer.Option(..., "--approved-by", help="Name of approver")
) -> None:
    from agentcomos.manual_os.approval import approve_request
    try:
        approve_request(run, task, approved_by)
        print(f"Manual OS request approved for {task} in {run}.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@manual_os_app.command("reject")
def manual_os_reject_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    rejected_by: str = typer.Option(..., "--rejected-by", help="Name of rejector"),
    reason: str = typer.Option(..., "--reason", help="Reason for rejection")
) -> None:
    from agentcomos.manual_os.approval import reject_request
    try:
        reject_request(run, task, rejected_by, reason)
        print(f"Manual OS request rejected for {task} in {run}.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@manual_os_app.command("result")
def manual_os_result_cmd(
    run: str = typer.Option(..., "--run", help="Run ID"),
    task: str = typer.Option(..., "--task", help="Task ID"),
    status: str = typer.Option(..., "--status", help="Status: completed, failed, skipped"),
    executed_by: str = typer.Option(..., "--executed-by", help="Name of executor"),
    summary: str = typer.Option(..., "--summary", help="Execution summary")
) -> None:
    from agentcomos.manual_os.result import report_result
    try:
        report_result(run, task, status, executed_by, summary)
        print(f"Manual OS result reported for {task} in {run}.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@manual_os_app.command("audit")
def manual_os_audit_cmd(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.manual_os.audit import generate_audit
    try:
        generate_audit(run)
        print(f"Manual OS audit generated for {run}.")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@gm_discord_app.command("ingest")
def gm_discord_ingest(
    run: str = typer.Option(..., "--run", help="Run ID"),
    message_file: str = typer.Option(..., "--message-file", help="Path to inbound message file"),
    fake: bool = typer.Option(False, "--fake", help="Must be true for G11")
) -> None:
    if not fake:
        raise typer.BadParameter("G11 requires --fake")
    from agentcomos.gm_discord.ingest import ingest_message
    try:
        path = ingest_message(run, message_file, fake)
        print(f"Message ingested: {path}")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@gm_discord_app.command("parse")
def gm_discord_parse(
    run: str = typer.Option(..., "--run", help="Run ID"),
    message: str = typer.Option(..., "--message", help="Message ID")
) -> None:
    from agentcomos.gm_discord.parser import parse_message
    try:
        path = parse_message(run, message)
        print(f"Command parsed: {path}")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@gm_discord_app.command("execute")
def gm_discord_execute(
    run: str = typer.Option(..., "--run", help="Run ID"),
    command: str = typer.Option(..., "--command", help="Command ID"),
    confirm: str = typer.Option(None, "--confirm", help="Confirmation type, e.g. explicit")
) -> None:
    from agentcomos.gm_discord.executor import execute_command
    try:
        path = execute_command(run, command, confirm)
        print(f"Command executed: {path}")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@gm_discord_app.command("status")
def gm_discord_status(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.gm_discord.status import get_gm_discord_status
    import yaml
    try:
        print(yaml.dump(get_gm_discord_status(run), sort_keys=False))
    except ValueError as e:
        raise typer.BadParameter(str(e))

@gm_discord_app.command("audit")
def gm_discord_audit(run: str = typer.Option(..., "--run", help="Run ID")) -> None:
    from agentcomos.gm_discord.audit import generate_audit
    try:
        path = generate_audit(run)
        print(f"Audit generated: {path}")
    except ValueError as e:
        raise typer.BadParameter(str(e))

@discord_app.command("status")
def discord_status(connect_check: bool = typer.Option(False, "--connect-check", help="Check gateway connection")) -> None:
    """Show the status of the Discord adapter."""
    from agentcomos.discord_adapter import status_check
    import yaml
    import asyncio
    print(yaml.dump(asyncio.run(status_check(connect_check)), sort_keys=False))

@discord_app.command("ingest-test")
def discord_ingest_test(
    message_file: Path = typer.Option(..., "--message-file", help="Path to inbound message file"),
    runtime_dir: Path = typer.Option(..., "--runtime-dir", help="Path to runtime dir")
) -> None:
    """Ingest a message for testing the Discord adapter."""
    from agentcomos.discord_adapter import ingest_test
    import yaml
    try:
        data = yaml.safe_load(message_file.read_text(encoding="utf-8"))
        result = ingest_test(data, runtime_dir)
        print(yaml.dump(result, sort_keys=False))
    except Exception as e:
        raise typer.BadParameter(str(e))

@discord_app.command("serve")
def discord_serve(
    runtime_dir: Path = typer.Option(Path(".agentcomos/runs/discord_runtime"), "--runtime-dir", help="Path to runtime dir"),
) -> None:
    """Serve the real Discord bot runtime."""
    import asyncio
    from agentcomos.discord_runtime import serve_discord
    
    try:
        result = asyncio.run(serve_discord(runtime_dir))
        if result.get("status") == "unavailable":
            print(f"Discord adapter unavailable: {result.get('reason')}")
            # Exit 0 because being disabled or lacking token shouldn't crash the deploy loop
            import sys
            sys.exit(0)
    except Exception as e:
        raise typer.BadParameter(str(e))

@app.command("healthcheck")
def healthcheck() -> None:
    """AgentComOS healthcheck."""
    import os
    data = {
        "status": "ok",
        "component": "agentcomos",
        "mode": "healthcheck",
        "runtime_dir": os.environ.get("AGENTCOMOS_RUNTIME_DIR", "/app/.agentcomos/runs"),
        "log_dir": os.environ.get("AGENTCOMOS_LOG_DIR", "/app/logs"),
        "report_dir": os.environ.get("AGENTCOMOS_REPORT_DIR", "/app/reports")
    }
    import builtins
    builtins.print(json.dumps(data))

executor_app = typer.Typer(help="Controlled Executor operations")
app.add_typer(executor_app, name="executor")

adapter_app = typer.Typer(help="Operation Adapter operations")
app.add_typer(adapter_app, name="adapter")

@executor_app.command("status")
def executor_status_cmd() -> None:
    from agentcomos.executor_config import ExecutorConfig
    import yaml
    
    config = ExecutorConfig()
    status = {
        "enabled": config.is_enabled(),
        "mode": config.get_mode(),
        "dry_run_only": config.is_dry_run_only(),
        "default_decision": config.get_default_decision(),
        "real_execution_available": False,
        "adapters_available": False,
        "dry_run_available": config.is_enabled() or config.get_mode() == "dry_run",
    }
    print(yaml.dump(status, sort_keys=False))

@executor_app.command("evaluate")
def executor_evaluate_cmd(
    request_file: Path = typer.Option(..., "--request-file", help="Path to executor request YAML"),
    runtime_dir: Path = typer.Option(..., "--runtime-dir", help="Directory to output artifacts")
) -> None:
    from agentcomos.executor_config import ExecutorConfig
    from agentcomos.executor_policy import ExecutorPolicy
    from agentcomos.executor_request import ExecutorRequest
    from agentcomos.executor_framework import ExecutorFramework
    from agentcomos.executor_redaction import redact_executor_data
    import yaml
    
    config = ExecutorConfig()
    policy = ExecutorPolicy.load(config.policy_path) if config.policy_path else None
    framework = ExecutorFramework(config, policy)
    
    try:
        request = ExecutorRequest.load_artifact(str(request_file))
        decision = framework.evaluate(request)
        
        import os
        os.makedirs(str(runtime_dir), exist_ok=True)
        request.write_artifact(str(runtime_dir / f"executor_request_{request.executor_request_id}.yaml"))
        decision.write_artifact(str(runtime_dir / f"executor_decision_{decision.decision_id}.yaml"))
        
        summary = redact_executor_data({
            "executor_request_id": request.executor_request_id,
            "decision": decision.decision,
            "reason": decision.reason,
            "risk_level": decision.risk_level,
        })
        print(yaml.dump(summary, sort_keys=False))
    except Exception as e:
        raise typer.BadParameter(str(e))

@executor_app.command("run-dry")
def executor_run_dry_cmd(
    request_file: Path = typer.Option(..., "--request-file", help="Path to executor request YAML"),
    runtime_dir: Path = typer.Option(..., "--runtime-dir", help="Directory to output artifacts")
) -> None:
    from agentcomos.executor_config import ExecutorConfig
    from agentcomos.executor_policy import ExecutorPolicy
    from agentcomos.executor_request import ExecutorRequest
    from agentcomos.executor_framework import ExecutorFramework
    from agentcomos.executor_redaction import redact_executor_data
    import yaml
    
    config = ExecutorConfig()
    policy = ExecutorPolicy.load(config.policy_path) if config.policy_path else None
    framework = ExecutorFramework(config, policy)
    
    try:
        request = ExecutorRequest.load_artifact(str(request_file))
        decision, result = framework.process_request(request, str(runtime_dir))
        
        summary = redact_executor_data({
            "executor_request_id": request.executor_request_id,
            "decision": decision.decision,
            "result_status": result.status,
            "execution_mode": result.execution_mode
        })
        print(yaml.dump(summary, sort_keys=False))
    except Exception as e:
        raise typer.BadParameter(str(e))

@adapter_app.command("status")
def adapter_status_cmd() -> None:
    from agentcomos.adapters import registry
    import yaml
    
    status = {}
    for name, adapter in registry.list_adapters().items():
        status[name] = {
            "adapter_type": adapter.adapter_type,
            "enabled": adapter.enabled,
            "dry_run_available": True,
            "mock_runner_available": True,
            "real_execution_available": False,
            "policy_required": adapter.policy_required,
            "approval_required_for_high_risk": adapter.approval_required_for_high_risk,
            "default_timeout_seconds": adapter.default_timeout_seconds,
            "supports_real_run": adapter.supports_real_run,
            "supports_dry_run": adapter.supports_dry_run,
        }
    print(yaml.dump({"adapters": status}, sort_keys=False))

@adapter_app.command("validate-policy")
def adapter_validate_policy_cmd(
    policy_file: Path = typer.Option(..., "--policy-file", help="Path to policy YAML")
) -> None:
    from agentcomos.operation_adapter_policy import OperationAdapterPolicyResolver
    import yaml
    
    try:
        with open(policy_file, "r") as f:
            policy_data = yaml.safe_load(f)
        resolver = OperationAdapterPolicyResolver(policy_data)
        
        status = {"valid": True, "adapters": {}}
        from agentcomos.adapters import registry
        for name, adapter in registry.list_adapters().items():
            if resolver.is_adapter_enabled(name):
                status["adapters"][name] = "enabled"
            else:
                status["adapters"][name] = "disabled"
                
        print(yaml.dump(status, sort_keys=False))
    except Exception as e:
        raise typer.BadParameter(str(e))

@adapter_app.command("dry-run")
def adapter_dry_run_cmd(
    request_file: Path = typer.Option(..., "--request-file", help="Path to executor request YAML"),
    runtime_dir: Path = typer.Option(..., "--runtime-dir", help="Directory to output artifacts")
) -> None:
    # Just redirect to executor run-dry, since it now includes adapter dry-run
    executor_run_dry_cmd(request_file, runtime_dir)

@executor_app.command("run-real")
def executor_run_real_cmd(
    request_file: Path = typer.Option(..., "--request-file", help="Path to executor request YAML"),
    runtime_dir: Path = typer.Option(..., "--runtime-dir", help="Directory to output artifacts")
) -> None:
    from agentcomos.executor_config import ExecutorConfig
    from agentcomos.executor_policy import ExecutorPolicy
    from agentcomos.executor_request import ExecutorRequest
    from agentcomos.executor_framework import ExecutorFramework
    from agentcomos.executor_redaction import redact_executor_data
    import yaml
    
    config = ExecutorConfig()
    policy = ExecutorPolicy.load(config.policy_path) if config.policy_path else None
    framework = ExecutorFramework(config, policy)
    
    try:
        request = ExecutorRequest.load_artifact(str(request_file))
        request.metadata["real_execution"] = True
        decision, result = framework.process_request(request, str(runtime_dir))
        
        summary = redact_executor_data({
            "executor_request_id": request.executor_request_id,
            "decision": decision.decision,
            "result_status": result.status,
            "execution_mode": result.execution_mode,
            "adapter_invoked": result.adapter_invoked,
            "adapter_type": result.adapter_type
        })
        print(yaml.dump(summary, sort_keys=False))
    except Exception as e:
        raise typer.BadParameter(str(e))

if __name__ == "__main__":
    app()
