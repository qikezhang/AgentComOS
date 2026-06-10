from typing import Dict, Any, Tuple, Optional
from ..operation_adapter_base import OperationAdapterBase
from ..operation_adapter_result import OperationAdapterResult
from ..executor_request import ExecutorRequest

class SshAdapter(OperationAdapterBase):
    adapter_type = "ssh"
    
    def validate_request(self, request: ExecutorRequest, policy: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        command_ref = request.metadata.get("command_ref")
        host_ref = request.metadata.get("host_ref")
        if not command_ref:
            return False, "missing_command_ref", None
        if not host_ref:
            return False, "missing_host_ref", None
            
        allowed_hosts = policy.get("allowed_hosts", [])
        host_config = next((h for h in allowed_hosts if h.get("host") == host_ref), None)
        if not host_config:
            return False, "unknown_host", None
            
        allowed_commands = policy.get("allowed_commands", [])
        if not allowed_commands:
            allowed_commands = policy.get("allow", [])
            
        cmd_config = next((c for c in allowed_commands if c.get("id") == command_ref or c.get("command_ref") == command_ref), None)
        if not cmd_config:
            return False, "command_not_allowed", None
            
        template = cmd_config.get("template")
        if not template:
            return False, "missing_template", None
            
        params = request.metadata.get("params", {})
        rendered = self.render_command_template(template, params)
        redacted_rendered = self.redact_output(rendered)
        
        return True, "valid", f"ssh {host_config.get('user', 'root')}@{host_ref} '{redacted_rendered}'"

    def dry_run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=request.metadata.get("command_ref"),
                status="blocked",
                reason=reason
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=request.metadata.get("command_ref"),
            rendered_command_redacted=rendered,
            status="dry_run_completed",
            execution_mode="dry_run",
            stdout_redacted="[DRY-RUN] ssh adapter execution simulated",
            exit_code=0
        )
        
    def run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        is_valid, reason, rendered = self.validate_request(request, policy)
        if not is_valid:
            return OperationAdapterResult(
                executor_request_id=request.executor_request_id,
                adapter_type=self.adapter_type,
                command_ref=request.metadata.get("command_ref"),
                status="blocked",
                reason=reason,
                real_execution=True
            )
            
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            command_ref=request.metadata.get("command_ref"),
            rendered_command_redacted=rendered,
            status="completed",
            execution_mode="real",
            real_execution=True,
            stdout_redacted="[MOCK-RUN] ssh adapter execution simulated safely",
            exit_code=0
        )
