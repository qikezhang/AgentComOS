from typing import Dict, Any, Optional, Tuple
from .operation_adapter_result import OperationAdapterResult
from .executor_request import ExecutorRequest
from .operation_adapter_redaction import redact_adapter_text

class OperationAdapterBase:
    adapter_type = "unknown"
    enabled = False
    supports_dry_run = True
    supports_real_run = False
    policy_required = True
    approval_required_for_high_risk = True
    default_timeout_seconds = 30
    
    def validate_request(self, request: ExecutorRequest, policy: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Returns (is_valid, reason, rendered_command)."""
        return False, "Not implemented", None

    def render_command_template(self, template: str, params: Dict[str, Any]) -> str:
        from .operation_adapter_templates import OperationAdapterTemplates
        return OperationAdapterTemplates.render(template, params)

    def redact_output(self, text: str) -> str:
        return redact_adapter_text(text)
        
    def dry_run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            status="blocked",
            reason="not_implemented"
        )
        
    def run(self, request: ExecutorRequest, policy: Dict[str, Any]) -> OperationAdapterResult:
        return OperationAdapterResult(
            executor_request_id=request.executor_request_id,
            adapter_type=self.adapter_type,
            status="blocked",
            reason="not_implemented"
        )
