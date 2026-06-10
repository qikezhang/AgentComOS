from typing import Dict, Optional
from .operation_adapter_base import OperationAdapterBase

class AdapterRegistry:
    def __init__(self):
        self._adapters: Dict[str, OperationAdapterBase] = {}

    def register(self, adapter: OperationAdapterBase):
        self._adapters[adapter.adapter_type] = adapter

    def get_adapter(self, adapter_type: str) -> Optional[OperationAdapterBase]:
        return self._adapters.get(adapter_type)

    def list_adapters(self) -> Dict[str, OperationAdapterBase]:
        return self._adapters.copy()

registry = AdapterRegistry()
