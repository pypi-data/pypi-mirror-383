# Copyright (c) 2025 Kim Jarvis TPF Software Services S.A. kim.jarvis@tpfsystems.com 
# This software is licensed under the MIT License. See the LICENSE file for details.
#
from reemote.command import Command
class Stop:
    """
    A class to manage lxc operations from the local host.

    Attributes:
        vm (str): Name of the virtual machine
        sudo (bool): If `True`, the commands will be executed with `sudo` privileges.
        su (bool): If `True`, the commands will be executed with `su` privileges.

    **Examples:**

    .. code:: python

        yield Stop(vm='debian-vm2')

    Usage:
        Stop container.

    Notes:
        - Commands are constructed based on the `present`, `sudo`, and `su` flags.
        - The `changed` flag is set if the package state changes after execution.
    """

    def __init__(self,
                 vm: str,
                 sudo: bool = False,
                 su: bool = False):
        self.vm = vm
        self.sudo: bool = sudo
        self.su: bool = su

    def __repr__(self) -> str:
        return (f"Stop("
                f"vm={self.vm!r}, "
                f"sudo={self.sudo!r}, "
                f"su={self.su!r}"
                f")")

    def execute(self):
        from reemote.operations.server.shell import Shell
        yield Shell(f"lxc stop {self.vm}",sudo=self.sudo,su=self.su)
