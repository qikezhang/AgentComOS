from ..operation_adapter_registry import registry
from .shell_adapter import ShellAdapter
from .ssh_adapter import SshAdapter
from .sudo_adapter import SudoAdapter
from .docker_adapter import DockerAdapter
from .systemctl_adapter import SystemctlAdapter

registry.register(ShellAdapter())
registry.register(SshAdapter())
registry.register(SudoAdapter())
registry.register(DockerAdapter())
registry.register(SystemctlAdapter())
