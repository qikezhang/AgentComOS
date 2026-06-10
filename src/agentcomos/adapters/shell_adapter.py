from typing import Dict, Any, Tuple, Optional
from ..operation_adapter_base import OperationAdapterBase
from ..operation_adapter_result import OperationAdapterResult
from ..executor_request import ExecutorRequest

class ShellAdapter(OperationAdapterBase):
    adapter_type = "shell"
    
    def validate_request(self, request: ExecutorRequest, policy: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        command_ref = request.metadata.get("command_ref")
        if not command_ref:
            return False, "missing_command_ref", None
            
        allowed_commands = policy.get("allowed_commands", [])
        if not allowed_commands:
            allowed_commands = policy.get("allow", [])
            
        cmd_config = next((c for c in allowed_commands if c.get("id") == command_ref or c.get("command_ref") == command_ref), None)
        if not cmd_config:
            return False, "command_not_allowed", None
            
        template = cmd_config.get("template")
        if not template:
            return False, "missing_template", None
            
        params = request.metadata.get("params")
        if params is None:
            params = {k: v for k, v in request.metadata.items() if k not in ["adapter_type", "real_execution", "command_ref"]}
        if params:
            for val in params.values():
                val_lower = str(val).lower()
                if any(p in val_lower for p in ["rm -rf", "|", ">", "<", "$(", "`", "&&", ";"]):
                    return False, "raw_command_blocked", None
                    
        rendered = self.render_command_template(template, params)
        
        # Validate rendered command
        dangerous_patterns = [
            "rm -rf", "bash -c", "sh -c", "zsh -c", "|", ">", "<", "$(", "`", "&&", ";",
            "sudo ", "ssh ", "systemctl ", "docker system prune", "docker run --privileged",
            "cat /etc/passwd", "printenv", "env", "secret", "token"
        ]
        rendered_lower = rendered.lower()
        for pattern in dangerous_patterns:
            if pattern in rendered_lower:
                return False, "rendered_command_blocked", None
                
        redacted_rendered = self.redact_output(rendered)
        
        return True, "valid", redacted_rendered

    def dry_run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=request.metadata.get("command_ref"),
                status="blocked",
                execution_mode="blocked",
                reason=reason
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=request.metadata.get("command_ref"),
            rendered_command_redacted=rendered,
            status="dry_run_completed",
            execution_mode="dry_run",
            stdout_redacted="[DRY-RUN] shell adapter execution simulated",
            exit_code=0
        )
        
    def run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        cmd_ref = getattr(request, "command_ref", None) or request.metadata.get("command_ref")
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=cmd_ref,
                status="blocked",
                execution_mode="blocked",
                reason=reason,
                real_execution=False
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=cmd_ref,
            rendered_command_redacted=rendered,
            status="mock_completed",
            execution_mode="mock",
            real_execution=False,
            stdout_redacted="[MOCK-RUN] shell adapter execution simulated safely",
            exit_code=0
        )
