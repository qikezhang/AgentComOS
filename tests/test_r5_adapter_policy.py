from agentcomos.operation_adapter_policy import OperationAdapterPolicyResolver

def test_policy_resolver():
    policy = {
        "adapters": {
            "shell": {
                "enabled": True,
                "allow": [{"id": "cmd1", "command_ref": "cmd1"}]
            }
        }
    }
    resolver = OperationAdapterPolicyResolver(policy)
    assert resolver.is_adapter_enabled("shell")
    assert not resolver.is_adapter_enabled("docker")
    assert resolver.get_command_config("shell", "cmd1") is not None
