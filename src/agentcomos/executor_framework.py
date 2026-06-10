import os
import datetime
import yaml
from typing import Optional, Tuple

from .executor_config import ExecutorConfig
from .executor_policy import ExecutorPolicy
from .executor_request import ExecutorRequest
from .executor_decision import ExecutorDecision
from .executor_result import ExecutorResult
from .executor_classifier import ExecutorClassifier

class ExecutorFramework:
    def __init__(self, config: ExecutorConfig, policy: Optional[ExecutorPolicy] = None):
        self.config = config
        self.policy = policy

    def evaluate(self, request: ExecutorRequest) -> ExecutorDecision:
        if not self.config.is_enabled():
            return ExecutorDecision(
                executor_request_id=request.executor_request_id,
                decision="blocked",
                reason="executor_disabled",
                requires_adapter=False,
                correlation_id=request.correlation_id,
                source=request.source
            )

        if not self.policy:
            return ExecutorDecision(
                executor_request_id=request.executor_request_id,
                decision="blocked",
                reason="policy_missing",
                requires_adapter=False,
                correlation_id=request.correlation_id,
                source=request.source
            )

        # 1. Classify the command text
        risk_level, initial_status, reason = ExecutorClassifier.classify_command(request.command_text_redacted)
        request.risk_level = risk_level
        request.status = initial_status

        request.command_text_redacted = ExecutorClassifier.redact(request.command_text_redacted)
        redaction_applied = "REDACTED" in request.command_text_redacted

        if initial_status == "blocked":
            return ExecutorDecision(
                executor_request_id=request.executor_request_id,
                decision="blocked",
                reason=reason,
                risk_level=risk_level,
                requires_adapter=False,
                policy_ref=self.policy.policy_id,
                redaction_applied=redaction_applied,
                correlation_id=request.correlation_id,
                source=request.source
            )

        # 2. Check policy source allowed
        if not self.policy.is_source_allowed(request.source):
            return ExecutorDecision(
                executor_request_id=request.executor_request_id,
                decision="blocked",
                reason="source_not_allowed",
                risk_level=risk_level,
                requires_adapter=False,
                policy_ref=self.policy.policy_id,
                redaction_applied=redaction_applied,
                correlation_id=request.correlation_id,
                source=request.source
            )

        # 3. Check risk and approval
        requires_approval = False
        if risk_level in ["high", "destructive"]:
            if self.config.requires_approval_for_high_risk():
                requires_approval = True
        
        # Determine adapter required based on command type (naive approach for R4)
        adapter_type = "unknown"
        if risk_level == "direct_system" or request.command_type == "docker_compose_restart":
            adapter_type = "docker"

        # In R4, real execution is always blocked or dry-run, so we return unsupported_adapter or dry_run
        decision_status = "allowed_dry_run"
        if requires_approval:
            decision_status = "requires_approval"

        return ExecutorDecision(
            executor_request_id=request.executor_request_id,
            decision=decision_status,
            reason=reason,
            risk_level=risk_level,
            requires_approval=requires_approval,
            requires_adapter=True,
            adapter_type=adapter_type,
            policy_ref=self.policy.policy_id,
            redaction_applied=redaction_applied,
            correlation_id=request.correlation_id,
            source=request.source
        )

    def execute_dry_run(self, request: ExecutorRequest, decision: ExecutorDecision) -> ExecutorResult:
        if decision.decision == "blocked":
            status = "blocked"
        elif decision.decision == "requires_approval":
            status = "requires_approval"
        elif decision.decision == "unsupported_adapter":
            status = "unsupported_adapter"
        elif decision.decision == "executor_disabled":
            status = "executor_disabled"
        else:
            status = "dry_run_completed"

        summary = f"Dry run: {request.command_text_redacted}"
        if status == "blocked":
            summary = f"Blocked: {decision.reason}"

        return ExecutorResult(
            executor_request_id=request.executor_request_id,
            decision_id=decision.decision_id,
            status=status,
            execution_mode="dry_run",
            real_execution=False,
            adapter_invoked=False,
            summary=summary,
            timeout_seconds=self.config.get_timeout_seconds(),
            redaction_applied=decision.redaction_applied,
            correlation_id=request.correlation_id,
            source=request.source
        )

    def process_request(self, request: ExecutorRequest, runtime_dir: str) -> Tuple[ExecutorDecision, ExecutorResult]:
        decision = self.evaluate(request)
        result = self.execute_dry_run(request, decision)

        # Write artifacts
        os.makedirs(runtime_dir, exist_ok=True)
        request.write_artifact(os.path.join(runtime_dir, f"executor_request_{request.executor_request_id}.yaml"))
        decision.write_artifact(os.path.join(runtime_dir, f"executor_decision_{decision.decision_id}.yaml"))
        result.write_artifact(os.path.join(runtime_dir, f"executor_result_{result.executor_result_id}.yaml"))

        # Write audit
        self.write_audit(request, decision, result, runtime_dir)

        return decision, result

    def write_audit(self, request: ExecutorRequest, decision: ExecutorDecision, result: ExecutorResult, runtime_dir: str):
        audit_file = os.path.join(runtime_dir, "executor_audit.yaml")
        audit_record = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": request.correlation_id,
            "source": request.source,
            "command_text_redacted": request.command_text_redacted,
            "decision": decision.decision,
            "reason": decision.reason,
            "result_status": result.status
        }
        mode = "a" if os.path.exists(audit_file) else "w"
        with open(audit_file, mode, encoding="utf-8") as f:
            yaml.dump([audit_record], f, default_flow_style=False, sort_keys=False)
