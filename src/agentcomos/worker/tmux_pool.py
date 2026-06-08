from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex
import shutil
import subprocess
import sys


@dataclass(frozen=True)
class TmuxStartResult:
    status: str
    session_name: str
    command: str | None = None
    reason: str | None = None


def tmux_path() -> str | None:
    return shutil.which("tmux")


def tmux_available() -> bool:
    return tmux_path() is not None


def session_exists(session_name: str) -> bool:
    if not tmux_available():
        return False
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def build_fake_worker_shell_command(
    *,
    invocation: Path,
    stdout_log: Path,
    stderr_log: Path,
    worktree: Path,
) -> str:
    python = shlex.quote(sys.executable)
    script = shlex.quote(str(worktree / "scripts" / "fake_hermes_worker.py"))
    invocation_arg = shlex.quote(str(invocation))
    stdout_arg = shlex.quote(str(stdout_log))
    stderr_arg = shlex.quote(str(stderr_log))
    src_path = shlex.quote(str(worktree / "src"))
    return (
        f"cd {shlex.quote(str(worktree))} && "
        f"PYTHONPATH={src_path} {python} {script} --invocation {invocation_arg} "
        f">> {stdout_arg} 2>> {stderr_arg}"
    )


def start_fake_worker_session(
    *,
    session_name: str,
    invocation: Path,
    stdout_log: Path,
    stderr_log: Path,
    worktree: Path,
) -> TmuxStartResult:
    if not tmux_available():
        return TmuxStartResult(
            status="unavailable",
            session_name=session_name,
            reason="tmux not found on PATH",
        )

    command = build_fake_worker_shell_command(
        invocation=invocation,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=worktree,
    )
    if session_exists(session_name):
        return TmuxStartResult(status="existing", session_name=session_name, command=command)

    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name, command],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return TmuxStartResult(
            status="failed",
            session_name=session_name,
            command=command,
            reason=(result.stderr or result.stdout or "tmux new-session failed").strip(),
        )
    return TmuxStartResult(status="started", session_name=session_name, command=command)


def kill_session(session_name: str) -> str:
    if not tmux_available():
        return "tmux unavailable"
    if not session_exists(session_name):
        return "session not found"
    result = subprocess.run(
        ["tmux", "kill-session", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError((result.stderr or result.stdout or "tmux kill-session failed").strip())
    return "session killed"

