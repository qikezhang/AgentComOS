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
from .executor_redaction import redact_executor_data
from .adapters import registry
from .operation_adapter_policy import OperationAdapterPolicyResolver

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
                risk_level=request.risk_level,
                requires_adapter=False,
                correlation_id=request.correlation_id,
                source=request.source
            )

        if not self.policy:
            return ExecutorDecision(
                executor_request_id=request.executor_request_id,
                decision="blocked",
                reason="policy_missing",
                risk_level=request.risk_level,
                requires_adapter=False,
                correlation_id=request.correlation_id,
                source=request.source
            )

        # 1. Use the pre-classified risk_level and reason from the request.
        # If it's unknown, we fallback to classifying the redacted text.
        if request.risk_level == "unknown" or request.risk_level is None:
            risk_level, initial_status, reason = ExecutorClassifier.classify_command(request.command_text_redacted)
            request.risk_level = risk_level
            request.status = initial_status
            if reason:
                request.reason = reason
        else:
            risk_level = request.risk_level
            initial_status = request.status
            reason = getattr(request, 'reason', None)

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
        
        # Determine adapter required based on metadata
        adapter_type = request.metadata.get("adapter_type", "unknown")
        if adapter_type == "unknown":
            if risk_level == "direct_system" or request.command_type == "docker_compose_restart":
                adapter_type = "docker"

        # Check adapter policy via resolver
        adapter_policy_resolver = None
        if self.policy and hasattr(self.policy, "get_raw_dict"):
            adapter_policy_resolver = OperationAdapterPolicyResolver(self.policy.get_raw_dict())

        # In R5, real execution is requested via metadata or config
        real_execution_requested = request.metadata.get("real_execution", False)
        
        # New logic: resolve real execution
        real_execution_allowed = real_execution_requested
        reason_for_block = None

        if real_execution_requested:
            if self.config.is_dry_run_only():
                real_execution_allowed = False
                reason_for_block = "dry_run_only"
            elif self.config.get_mode() == "dry_run":
                real_execution_allowed = False
                reason_for_block = "real_execution_disabled"

        if real_execution_requested and not real_execution_allowed:
            # metadata asked for real, but config denies -> block
            decision_status = "blocked"
            reason = reason_for_block or "real_execution_disabled"
        else:
            decision_status = "allowed_dry_run" if not real_execution_allowed else "allowed"

        if requires_approval and not request.requires_approval: 
            if decision_status != "blocked":
                decision_status = "requires_approval"

        if adapter_policy_resolver and not adapter_policy_resolver.is_adapter_enabled(adapter_type):
            if decision_status not in ["blocked", "requires_approval"]:
                decision_status = "adapter_disabled"
                
        # If policy for adapter is missing completely
        if adapter_policy_resolver and not adapter_policy_resolver.get_adapter_config(adapter_type):
             if decision_status != "blocked":
                 decision_status = "adapter_policy_missing"
                 
        # Check raw command gate (PART D)
        # 1. Requests without command_ref must be blocked.
        # 2. Requests containing raw_command or freeform command must be blocked.
        if decision_status not in ["adapter_disabled", "adapter_policy_missing", "requires_approval", "blocked"]:
            if getattr(request, "raw_command_present", False):
                 decision_status = "blocked"
                 reason = "raw_command_blocked"
            elif not getattr(request, "command_ref", None) and not request.metadata.get("command_ref"):
                 decision_status = "blocked"
                 reason = "command_ref_missing"
                 
        # Command Ref Policy Gate & Timeout Gate
        if decision_status not in ["adapter_disabled", "adapter_policy_missing", "requires_approval", "blocked"]:
            cmd_ref = getattr(request, "command_ref", None) or request.metadata.get("command_ref")
            cmd_config = adapter_policy_resolver.get_command_config(adapter_type, cmd_ref) if adapter_policy_resolver else None
            if not cmd_config:
                 decision_status = "blocked"
                 reason = "command_ref_not_allowed"
            elif "timeout_seconds" not in cmd_config:
                 decision_status = "blocked"
                 reason = "timeout_required"

        # Additional gate: secrets
        if decision_status not in ["adapter_disabled", "adapter_policy_missing", "requires_approval", "blocked"]:
            if request.command_type == "secret_request" or request.risk_level == "secret":
                 decision_status = "blocked"
                 reason = "secret_request_blocked"

        # Apply privileged systemctl action detector here
        if adapter_type == "systemctl" and decision_status not in ["adapter_disabled", "adapter_policy_missing", "blocked"]:
            from .adapters.systemctl_adapter import is_privileged_systemctl_action
            
            cmd_ref = getattr(request, "command_ref", None) or request.metadata.get("command_ref")
            rendered_command = request.metadata.get("rendered_command", "")
            is_priv, priv_risk, priv_reason = is_privileged_systemctl_action(cmd_ref, rendered_command, request.metadata)
            
            if is_priv:
                requires_approval = True
                risk_level = priv_risk
                if not request.requires_approval:
                    decision_status = "requires_approval"
                    reason = priv_reason
                    
                # Ensure the allowlist does not bypass approval or allow unapproved overrides for privileged commands
                # Although allow_unapproved might be defined in policy, we strictly block it for systemctl privileged actions if missing real approval
                if getattr(self.policy, 'is_allow_unapproved_enabled', lambda: False)():
                    if not request.requires_approval:
                        decision_status = "blocked"
                        reason = priv_reason

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
        elif decision.decision == "adapter_disabled":
            status = "blocked"
            decision.reason = "adapter_disabled"
        elif decision.decision == "adapter_policy_missing":
            status = "blocked"
            decision.reason = "adapter_policy_missing"
        else:
            status = "dry_run_completed"

        adapter_invoked = False
        adapter_result = None
        
        if status == "dry_run_completed":
            adapter = registry.get_adapter(decision.adapter_type)
            if adapter:
                policy_dict = {}
                if self.policy and hasattr(self.policy, "get_raw_dict"):
                    policy_dict = OperationAdapterPolicyResolver(self.policy.get_raw_dict()).get_adapter_config(decision.adapter_type) or {}
                adapter_result = adapter.dry_run(request, policy_dict)
                adapter_invoked = True
                if adapter_result.status == "blocked":
                    status = "blocked"
                    decision.reason = adapter_result.reason
                else:
                    request.command_text_redacted = adapter_result.rendered_command_redacted or request.command_text_redacted

        summary = f"Dry run: {request.command_text_redacted}"
        if status == "blocked":
            summary = f"Blocked: {decision.reason}"

        kwargs = {}
        if adapter_result:
            kwargs["adapter_type"] = adapter_result.adapter_type
            kwargs["adapter_result_id"] = adapter_result.adapter_result_id
            kwargs["stdout_redacted"] = adapter_result.stdout_redacted
            kwargs["stderr_redacted"] = adapter_result.stderr_redacted
            kwargs["exit_code"] = adapter_result.exit_code

        return ExecutorResult(
            executor_request_id=request.executor_request_id,
            decision_id=decision.decision_id,
            status=status,
            execution_mode="dry_run",
            real_execution=False,
            adapter_invoked=adapter_invoked,
            summary=summary,
            timeout_seconds=self.config.get_timeout_seconds(),
            redaction_applied=decision.redaction_applied,
            correlation_id=request.correlation_id,
            source=request.source,
            **kwargs
        )

    def execute_real(self, request: ExecutorRequest, decision: ExecutorDecision) -> ExecutorResult:
        if decision.decision != "allowed":
            status = "blocked"
            if decision.decision == "requires_approval":
                status = "requires_approval"
            elif decision.decision in ["executor_disabled", "adapter_disabled", "adapter_policy_missing"]:
                status = "blocked"
                decision.reason = decision.decision
        else:
            status = "completed"

        adapter_invoked = False
        adapter_result = None
        
        if status == "completed":
            adapter = registry.get_adapter(decision.adapter_type)
            if adapter:
                policy_dict = {}
                if self.policy and hasattr(self.policy, "get_raw_dict"):
                    policy_dict = OperationAdapterPolicyResolver(self.policy.get_raw_dict()).get_adapter_config(decision.adapter_type) or {}
                adapter_result = adapter.run(request, policy_dict)
                adapter_invoked = True
                if adapter_result.status == "blocked":
                    status = "blocked"
                    decision.reason = adapter_result.reason
                else:
                    request.command_text_redacted = adapter_result.rendered_command_redacted or request.command_text_redacted

        summary = f"Executed: {request.command_text_redacted}"
        if status == "blocked":
            summary = f"Blocked: {decision.reason}"
        elif status == "requires_approval":
            summary = f"Requires approval: {decision.reason}"

        kwargs = {}
        real_exec = False
        exec_mode = "blocked" if status == "blocked" else "dry_run"
        
        if adapter_result:
            kwargs["adapter_type"] = adapter_result.adapter_type
            kwargs["adapter_result_id"] = adapter_result.adapter_result_id
            kwargs["stdout_redacted"] = adapter_result.stdout_redacted
            kwargs["stderr_redacted"] = adapter_result.stderr_redacted
            kwargs["exit_code"] = adapter_result.exit_code
            real_exec = adapter_result.real_execution
            exec_mode = adapter_result.execution_mode

        return ExecutorResult(
            executor_request_id=request.executor_request_id,
            decision_id=decision.decision_id,
            status=status,
            execution_mode=exec_mode,
            real_execution=real_exec,
            adapter_invoked=adapter_invoked,
            summary=summary,
            timeout_seconds=self.config.get_timeout_seconds(),
            redaction_applied=decision.redaction_applied,
            correlation_id=request.correlation_id,
            source=request.source,
            **kwargs
        )

    def process_request(self, request: ExecutorRequest, runtime_dir: str) -> Tuple[ExecutorDecision, ExecutorResult]:
        # Enforce global real execution config before anything else
        real_execution_requested = request.metadata.get("real_execution", False)
        if real_execution_requested:
            if self.config.is_dry_run_only() or self.config.get_mode() == "dry_run":
                request.metadata["real_execution"] = False
                
        decision = self.evaluate(request)
        real_execution_requested = request.metadata.get("real_execution", False)
        
        if real_execution_requested:
            result = self.execute_real(request, decision)
        else:
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
        audit_record = redact_executor_data({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": request.correlation_id,
            "source": request.source,
            "command_text_redacted": request.command_text_redacted,
            "decision": decision.decision,
            "reason": decision.reason,
            "result_status": result.status
        })
        mode = "a" if os.path.exists(audit_file) else "w"
        with open(audit_file, mode, encoding="utf-8") as f:
            yaml.dump([audit_record], f, default_flow_style=False, sort_keys=False)
