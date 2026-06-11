import os
import yaml
import datetime
from typing import Dict, Any
from .executor_request import ExecutorRequest
from .operation_adapter_result import OperationAdapterResult
from .operation_adapter_redaction import redact_adapter_data

class OperationAdapterAudit:
    @staticmethod
    def write_audit(request: ExecutorRequest, result: OperationAdapterResult, runtime_dir: str):
        audit_file = os.path.join(runtime_dir, "adapter_audit.yaml")
        audit_record = redact_adapter_data({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "executor_request_id": request.executor_request_id,
            "adapter_result_id": result.adapter_result_id,
            "adapter_type": result.adapter_type,
            "command_ref": result.command_ref,
            "rendered_command_redacted": result.rendered_command_redacted,
            "execution_mode": result.execution_mode,
            "real_execution": result.real_execution,
            "status": result.status,
            "reason": result.reason
        })
        mode = "a" if os.path.exists(audit_file) else "w"
        with open(audit_file, mode, encoding="utf-8") as f:
            yaml.dump([audit_record], f, default_flow_style=False, sort_keys=False)
