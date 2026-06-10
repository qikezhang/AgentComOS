import datetime
import uuid
import yaml
from typing import Dict, Any, Optional
from .executor_redaction import redact_executor_data


class ExecutorDecision:
    def __init__(
        self,
        executor_request_id: str,
        decision: str,
        reason: Optional[str] = None,
        risk_level: str = "unknown",
        requires_approval: bool = False,
        requires_adapter: bool = True,
        adapter_type: Optional[str] = None,
        execution_mode: str = "dry_run",
        policy_ref: Optional[str] = None,
        redaction_applied: bool = False,
        decision_id: Optional[str] = None,
        evaluated_at: Optional[str] = None,
        correlation_id: Optional[str] = None,
        source: str = "unknown",
    ):
        self.decision_id = decision_id or f"EXEC-DEC-{uuid.uuid4().hex[:8].upper()}"
        self.executor_request_id = executor_request_id
        self.decision = decision
        self.reason = reason
        self.risk_level = risk_level
        self.requires_approval = requires_approval
        self.requires_adapter = requires_adapter
        self.adapter_type = adapter_type
        self.execution_mode = execution_mode
        self.policy_ref = policy_ref
        self.redaction_applied = redaction_applied
        self.evaluated_at = evaluated_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.correlation_id = correlation_id or executor_request_id
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return redact_executor_data({
            "decision_id": self.decision_id,
            "executor_request_id": self.executor_request_id,
            "decision": self.decision,
            "reason": self.reason,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "requires_adapter": self.requires_adapter,
            "adapter_type": self.adapter_type,
            "execution_mode": self.execution_mode,
            "policy_ref": self.policy_ref,
            "redaction_applied": self.redaction_applied,
            "evaluated_at": self.evaluated_at,
            "correlation_id": self.correlation_id,
            "source": self.source,
        })

    def write_artifact(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
