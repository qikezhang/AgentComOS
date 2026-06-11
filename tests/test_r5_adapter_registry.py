from agentcomos.operation_adapter_registry import AdapterRegistry
from agentcomos.operation_adapter_base import OperationAdapterBase

def test_registry():
    registry = AdapterRegistry()
    adapter = OperationAdapterBase()
    adapter.adapter_type = "test_adapter"
    registry.register(adapter)
    
    assert registry.get_adapter("test_adapter") == adapter
    assert "test_adapter" in registry.list_adapters()
