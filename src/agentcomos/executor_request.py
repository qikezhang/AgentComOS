import datetime
import uuid
import yaml
from typing import Dict, Any, Optional
from .executor_redaction import redact_executor_data, redact_executor_text

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
        raw_command_present: bool = False,
        **kwargs
    ):
        self.executor_request_id = executor_request_id or f"EXEC-REQ-{uuid.uuid4().hex[:8].upper()}"
        self.source = redact_executor_text(source)
        self.source_message_id = redact_executor_text(source_message_id) if source_message_id else None
        self.requested_by_hash = requested_by_hash
        self.command_type = command_type
        self.command_text_redacted = redact_executor_text(command_text_redacted)
        self.target = redact_executor_text(target) if target else None
        self.risk_level = risk_level
        self.requires_executor = requires_executor
        self.requires_approval = requires_approval
        self.policy_ref = policy_ref
        self.correlation_id = correlation_id or self.executor_request_id
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.raw_command_present = raw_command_present
        self.metadata = redact_executor_data(kwargs) if kwargs else {}

    def to_dict(self) -> Dict[str, Any]:
        data = {
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
        if self.raw_command_present:
            data["raw_command_present"] = True
        if self.metadata:
            data.update(self.metadata)
        return redact_executor_data(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutorRequest":
        redacted_data = redact_executor_data(data)
        
        command_text_redacted = redacted_data.get("command_text_redacted", "")
        raw_command_present = False
        
        if "command_text" in data:
            raw_command_present = True
            if not command_text_redacted:
                command_text_redacted = redact_executor_text(data["command_text"])
                
        return cls(
            executor_request_id=redacted_data.get("executor_request_id"),
            source=redacted_data.get("source", "unknown"),
            source_message_id=redacted_data.get("source_message_id"),
            requested_by_hash=redacted_data.get("requested_by_hash", "unknown"),
            command_type=redacted_data.get("command_type", "unknown"),
            command_text_redacted=command_text_redacted,
            target=redacted_data.get("target"),
            risk_level=redacted_data.get("risk_level", "unknown"),
            requires_executor=redacted_data.get("requires_executor", True),
            requires_approval=redacted_data.get("requires_approval", False),
            policy_ref=redacted_data.get("policy_ref"),
            correlation_id=redacted_data.get("correlation_id"),
            status=redacted_data.get("status", "received"),
            created_at=redacted_data.get("created_at"),
            raw_command_present=raw_command_present,
            **(redacted_data.get("metadata", {}))
        )

    def write_artifact(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load_artifact(cls, file_path: str) -> "ExecutorRequest":
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return cls.from_dict(data)
