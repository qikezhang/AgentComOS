from agentcomos.operation_adapter_base import OperationAdapterBase

def test_redaction():
    adapter = OperationAdapterBase()
    text = "Secret token=123456"
    assert "123456" not in adapter.redact_output(text)
