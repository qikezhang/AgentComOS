import os

def test_no_operation_adapter_files():
    adapters = ["shell_adapter.py", "ssh_adapter.py", "sudo_adapter.py", "docker_adapter.py", "systemctl_adapter.py"]
    for adapter in adapters:
        assert not os.path.exists(os.path.join("src", "agentcomos", adapter))

def test_no_real_execution():
    pass # covered by bash script in validation
