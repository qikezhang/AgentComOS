from typing import Dict, Any, Optional

class OperationAdapterPolicyResolver:
    def __init__(self, policy: Dict[str, Any]):
        self.policy = policy

    def get_adapter_config(self, adapter_type: str) -> Optional[Dict[str, Any]]:
        adapters = self.policy.get("adapters", {})
        return adapters.get(adapter_type)

    def is_adapter_enabled(self, adapter_type: str) -> bool:
        config = self.get_adapter_config(adapter_type)
        if not config:
            return False
        return config.get("enabled", False)

    def get_command_config(self, adapter_type: str, command_id: str) -> Optional[Dict[str, Any]]:
        config = self.get_adapter_config(adapter_type)
        if not config:
            return None
            
        # Check deny list first
        denied_commands = config.get("denied_commands", [])
        if not denied_commands:
            denied_commands = config.get("deny", [])
            
        for cmd in denied_commands:
            cmd_id = cmd.get("id") or cmd.get("command_ref")
            if cmd_id == command_id:
                # Denied explicitly, override allow
                return None
                
        allowed_commands = config.get("allowed_commands", [])
        if not allowed_commands:
            allowed_commands = config.get("allow", [])
            
        for cmd in allowed_commands:
            cmd_id = cmd.get("id") or cmd.get("command_ref")
            if cmd_id == command_id:
                return cmd
                
        # systemctl specific: allowed_services and allowed_actions
        if adapter_type == "systemctl" and command_id:
            # We treat command_id as the action (status, restart, etc.)
            allowed_actions = config.get("allowed_actions", [])
            if command_id in allowed_actions:
                # the actual service validation happens in validate_request
                return {"id": command_id, "action": command_id}

        return None
