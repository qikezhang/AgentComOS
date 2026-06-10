import os
from typing import Optional

class ExecutorConfig:
    """Configuration for the Controlled Executor Framework."""
    def __init__(self) -> None:
        self.enabled: bool = os.environ.get("CONTROLLED_EXECUTOR_ENABLED", "false").lower() == "true"
        self.mode: str = os.environ.get("CONTROLLED_EXECUTOR_MODE", "disabled")
        self.policy_path: Optional[str] = os.environ.get("CONTROLLED_EXECUTOR_POLICY_PATH", None)
        self.default_decision: str = os.environ.get("CONTROLLED_EXECUTOR_DEFAULT_DECISION", "deny")
        self.require_approval_for_high_risk: bool = os.environ.get("CONTROLLED_EXECUTOR_REQUIRE_APPROVAL_FOR_HIGH_RISK", "true").lower() == "true"
        self.timeout_seconds: int = int(os.environ.get("CONTROLLED_EXECUTOR_TIMEOUT_SECONDS", "30"))
        self.audit_all: bool = os.environ.get("CONTROLLED_EXECUTOR_AUDIT_ALL", "true").lower() == "true"
        self.dry_run_only: bool = os.environ.get("CONTROLLED_EXECUTOR_DRY_RUN_ONLY", "true").lower() == "true"

    def is_enabled(self) -> bool:
        return self.enabled

    def get_mode(self) -> str:
        return self.mode

    def get_default_decision(self) -> str:
        return self.default_decision

    def requires_approval_for_high_risk(self) -> bool:
        return self.require_approval_for_high_risk

    def get_timeout_seconds(self) -> int:
        return self.timeout_seconds

    def should_audit_all(self) -> bool:
        return self.audit_all

    def is_dry_run_only(self) -> bool:
        return self.dry_run_only
