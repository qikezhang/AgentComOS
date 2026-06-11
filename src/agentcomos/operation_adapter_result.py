import datetime
import uuid
import yaml
from typing import Dict, Any, Optional

class OperationAdapterResult:
    def __init__(
        self,
        executor_request_id: str,
        adapter_type: str,
        command_ref: Optional[str] = None,
        rendered_command_redacted: Optional[str] = None,
        execution_mode: str = "dry_run",
        real_execution: bool = False,
        adapter_invoked: bool = True,
        status: str = "completed",
        exit_code: Optional[int] = None,
        stdout_redacted: Optional[str] = None,
        stderr_redacted: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        reason: Optional[str] = None,
        rollback_note: Optional[str] = None,
        redaction_applied: bool = True,
        adapter_result_id: Optional[str] = None
    ):
        self.adapter_result_id = adapter_result_id or f"ADAPT-RES-{uuid.uuid4().hex[:8].upper()}"
        self.executor_request_id = executor_request_id
        self.adapter_type = adapter_type
        self.command_ref = command_ref
        self.rendered_command_redacted = rendered_command_redacted
        self.execution_mode = execution_mode
        self.real_execution = real_execution
        self.adapter_invoked = adapter_invoked
        self.status = status
        self.exit_code = exit_code
        self.stdout_redacted = stdout_redacted
        self.stderr_redacted = stderr_redacted
        self.timeout_seconds = timeout_seconds
        self.started_at = started_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.finished_at = finished_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.reason = reason
        self.rollback_note = rollback_note
        self.redaction_applied = redaction_applied

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "adapter_result_id": self.adapter_result_id,
            "executor_request_id": self.executor_request_id,
            "adapter_type": self.adapter_type,
            "execution_mode": self.execution_mode,
            "real_execution": self.real_execution,
            "adapter_invoked": self.adapter_invoked,
            "status": self.status,
            "redaction_applied": self.redaction_applied,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
        if self.command_ref:
            data["command_ref"] = self.command_ref
        if self.rendered_command_redacted:
            data["rendered_command_redacted"] = self.rendered_command_redacted
        if self.exit_code is not None:
            data["exit_code"] = self.exit_code
        if self.stdout_redacted is not None:
            data["stdout_redacted"] = self.stdout_redacted
        if self.stderr_redacted is not None:
            data["stderr_redacted"] = self.stderr_redacted
        if self.timeout_seconds is not None:
            data["timeout_seconds"] = self.timeout_seconds
        if self.reason:
            data["reason"] = self.reason
        if self.rollback_note:
            data["rollback_note"] = self.rollback_note
        return data

