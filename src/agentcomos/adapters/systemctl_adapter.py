from typing import Dict, Any, Tuple, Optional
from ..operation_adapter_base import OperationAdapterBase
from ..operation_adapter_result import OperationAdapterResult
from ..executor_request import ExecutorRequest

def is_privileged_systemctl_action(command_ref: Optional[str], rendered_command: Optional[str], metadata: dict) -> Tuple[bool, str, str]:
    """
    Checks if a systemctl action is privileged.
    Returns (is_privileged, intrinsic_risk, reason)
    """
    bare_commands = {"restart", "stop", "start", "reload", "enable", "disable"}
    prefixed_commands = {"systemctl_" + cmd for cmd in bare_commands}
    
    if command_ref and (command_ref in bare_commands or command_ref in prefixed_commands):
        return True, "privileged", "privileged_approval_required"
        
    action = metadata.get("action")
    if action and (action in bare_commands or action in prefixed_commands):
        return True, "privileged", "privileged_approval_required"
        
    commands_to_check = []
    if rendered_command:
        commands_to_check.append(rendered_command)
    meta_rendered = metadata.get("rendered_command")
    if meta_rendered:
        commands_to_check.append(meta_rendered)
        
    for text in commands_to_check:
        for cmd in bare_commands:
            if f"systemctl {cmd}" in text:
                return True, "privileged", "privileged_approval_required"
                
    return False, "", ""

class SystemctlAdapter(OperationAdapterBase):
    adapter_type = "systemctl"
    
    def validate_request(self, request: ExecutorRequest, policy: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        if request.metadata.get('_command_ref_conflict'):
            return False, 'command_ref_conflict_blocked', None

        command_ref = request.command_ref
        service_ref = request.metadata.get("service_ref")
        
        if not command_ref:
            return False, "missing_command_ref", None
        if not service_ref:
            return False, "missing_service_ref", None
            
        allowed_services = policy.get("allowed_services", [])
        if service_ref not in allowed_services:
            return False, "service_not_allowed", None
            
        allowed_actions = policy.get("allowed_actions", [])
        if command_ref not in allowed_actions:
            return False, "action_not_allowed", None
            
        # Hardcoded templates for systemctl to ensure safety
        template = f"systemctl {command_ref} {service_ref}"
        rendered = self.render_command_template(template, {})
        redacted_rendered = self.redact_output(rendered)
        
        is_priv, priv_risk, priv_reason = is_privileged_systemctl_action(command_ref, rendered, request.metadata)
        if is_priv:
            if not request.metadata.get("approved"):
                return False, priv_reason, None
        
        return True, "valid", redacted_rendered

    def dry_run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=request.command_ref,
                status="blocked",
                execution_mode="blocked",
                reason=reason
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=request.command_ref,
            rendered_command_redacted=rendered,
            status="dry_run_completed",
            execution_mode="dry_run",
            stdout_redacted="[DRY-RUN] systemctl adapter execution simulated",
            exit_code=0
        )
        
    def run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=request.command_ref,
                status="blocked",
                execution_mode="blocked",
                reason=reason,
                real_execution=False
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=request.command_ref,
            rendered_command_redacted=rendered,
            status="mock_completed",
            execution_mode="mock",
            real_execution=False,
            stdout_redacted="[MOCK-RUN] systemctl adapter execution simulated safely",
            exit_code=0
        )
