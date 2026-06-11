import datetime
import uuid
import yaml
from typing import Dict, Any, Optional, List
from .executor_redaction import redact_executor_data

class ExecutorResult:
    def __init__(
        self,
        executor_request_id: str,
        decision_id: str,
        status: str,
        execution_mode: str = "dry_run",
        real_execution: bool = False,
        adapter_invoked: bool = False,
        summary: str = "",
        timeout_seconds: int = 30,
        redaction_applied: bool = False,
        artifacts: Optional[List[str]] = None,
        executor_result_id: Optional[str] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        correlation_id: Optional[str] = None,
        source: str = "unknown",
        **kwargs
    ):
        self.executor_result_id = executor_result_id or f"EXEC-RES-{uuid.uuid4().hex[:8].upper()}"
        self.executor_request_id = executor_request_id
        self.decision_id = decision_id
        self.status = status
        self.execution_mode = execution_mode
        self.real_execution = real_execution
        self.adapter_invoked = adapter_invoked
        self.adapter_type = kwargs.get("adapter_type")
        self.adapter_result_id = kwargs.get("adapter_result_id")
        self.stdout_redacted = kwargs.get("stdout_redacted")
        self.stderr_redacted = kwargs.get("stderr_redacted")
        self.rollback_note = kwargs.get("rollback_note")
        self.exit_code = kwargs.get("exit_code")
        self.summary = summary
        self.timeout_seconds = timeout_seconds
        self.redaction_applied = redaction_applied
        self.artifacts = artifacts or []
        self.started_at = started_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.finished_at = finished_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.correlation_id = correlation_id or executor_request_id
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "executor_result_id": self.executor_result_id,
            "executor_request_id": self.executor_request_id,
            "decision_id": self.decision_id,
            "status": self.status,
            "execution_mode": self.execution_mode,
            "real_execution": self.real_execution,
            "adapter_invoked": self.adapter_invoked,
            "summary": self.summary,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "timeout_seconds": self.timeout_seconds,
            "redaction_applied": self.redaction_applied,
            "artifacts": self.artifacts,
            "correlation_id": self.correlation_id,
            "source": self.source,
        }
        if self.adapter_type:
            data["adapter_type"] = self.adapter_type
        if self.adapter_result_id:
            data["adapter_result_id"] = self.adapter_result_id
        if self.stdout_redacted is not None:
            data["stdout_redacted"] = self.stdout_redacted
        if self.stderr_redacted is not None:
            data["stderr_redacted"] = self.stderr_redacted
        if self.rollback_note:
            data["rollback_note"] = self.rollback_note
        if self.exit_code is not None:
            data["exit_code"] = self.exit_code
            
        return redact_executor_data(data)

    def write_artifact(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
