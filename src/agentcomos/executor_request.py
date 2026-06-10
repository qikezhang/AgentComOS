import datetime
import uuid
import yaml
from typing import Dict, Any, Optional

class ExecutorRequest:
    """Model representing a requested controlled execution command."""
    def __init__(
        self,
        source: str,
        command_type: str,
        command_text_redacted: str,
        requested_by_hash: str = "unknown",
        source_message_id: Optional[str] = None,
        target: Optional[str] = None,
        risk_level: str = "unknown",
        requires_executor: bool = True,
        requires_approval: bool = False,
        policy_ref: Optional[str] = None,
        correlation_id: Optional[str] = None,
        status: str = "received",
        executor_request_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.executor_request_id = executor_request_id or f"EXEC-REQ-{uuid.uuid4().hex[:8].upper()}"
        self.source = source
        self.source_message_id = source_message_id
        self.requested_by_hash = requested_by_hash
        self.command_type = command_type
        self.command_text_redacted = command_text_redacted
        self.target = target
        self.risk_level = risk_level
        self.requires_executor = requires_executor
        self.requires_approval = requires_approval
        self.policy_ref = policy_ref
        self.correlation_id = correlation_id or self.executor_request_id
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executor_request_id": self.executor_request_id,
            "source": self.source,
            "source_message_id": self.source_message_id,
            "requested_by_hash": self.requested_by_hash,
            "command_type": self.command_type,
            "command_text_redacted": self.command_text_redacted,
            "target": self.target,
            "risk_level": self.risk_level,
            "requires_executor": self.requires_executor,
            "requires_approval": self.requires_approval,
            "policy_ref": self.policy_ref,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutorRequest":
        return cls(
            executor_request_id=data.get("executor_request_id"),
            source=data.get("source", "unknown"),
            source_message_id=data.get("source_message_id"),
            requested_by_hash=data.get("requested_by_hash", "unknown"),
            command_type=data.get("command_type", "unknown"),
            command_text_redacted=data.get("command_text_redacted", ""),
            target=data.get("target"),
            risk_level=data.get("risk_level", "unknown"),
            requires_executor=data.get("requires_executor", True),
            requires_approval=data.get("requires_approval", False),
            policy_ref=data.get("policy_ref"),
            correlation_id=data.get("correlation_id"),
            status=data.get("status", "received"),
            created_at=data.get("created_at"),
        )

    def write_artifact(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load_artifact(cls, file_path: str) -> "ExecutorRequest":
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return cls.from_dict(data)
