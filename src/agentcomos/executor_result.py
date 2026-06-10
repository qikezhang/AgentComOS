import datetime
import uuid
import yaml
from typing import Dict, Any, Optional, List

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
    ):
        self.executor_result_id = executor_result_id or f"EXEC-RES-{uuid.uuid4().hex[:8].upper()}"
        self.executor_request_id = executor_request_id
        self.decision_id = decision_id
        self.status = status
        self.execution_mode = execution_mode
        self.real_execution = real_execution
        self.adapter_invoked = adapter_invoked
        self.summary = summary
        self.timeout_seconds = timeout_seconds
        self.redaction_applied = redaction_applied
        self.artifacts = artifacts or []
        self.started_at = started_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.finished_at = finished_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.correlation_id = correlation_id or executor_request_id
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
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

    def write_artifact(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
