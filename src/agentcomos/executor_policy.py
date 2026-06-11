import yaml
import os
from typing import Dict, Any, Optional

class ExecutorPolicy:
    """Represents a loaded executor policy."""
    def __init__(self, policy_data: Dict[str, Any]):
        self.policy_id = policy_data.get("policy_id", "unknown")
        self.default_action = policy_data.get("default_action", "block")
        self.allowed_sources = set(policy_data.get("allowed_sources", []))
        self.adapters = policy_data.get("adapters", {})
        self.redaction_patterns = policy_data.get("redaction_patterns", [])

    @classmethod
    def load(cls, file_path: str) -> Optional["ExecutorPolicy"]:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not data:
                return None
            return cls(data)

    def is_source_allowed(self, source: str) -> bool:
        return source in self.allowed_sources

    def get_adapter_config(self, adapter_name: str) -> Optional[Dict[str, Any]]:
        return self.adapters.get(adapter_name)

    def evaluate_command(self, adapter_name: str, command_ref: str) -> bool:
        adapter_config = self.get_adapter_config(adapter_name)
        if not adapter_config or not adapter_config.get("enabled", False):
            return False
        
        # very simplified matching for R4 since we don't really execute
        if adapter_name == "shell" or adapter_name == "ssh" or adapter_name == "sudo" or adapter_name == "docker" or adapter_name == "systemctl":
            # R4 has no real adapters, execution is dry_run or blocked.
            pass

        return True  # actual policy logic would be more complex

    def get_raw_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "default_action": self.default_action,
            "allowed_sources": list(self.allowed_sources),
            "adapters": self.adapters,
            "redaction_patterns": self.redaction_patterns
        }
