# Copyright (c) 2025 Kim Jarvis TPF Software Services S.A. kim.jarvis@tpfsystems.com 
# This software is licensed under the MIT License. See the LICENSE file for details.
#
import asyncssh

import reemote.gui.functions.remove
from reemote.command import Command


class Remove:
    """
    A class to encapsulate the functionality of remove (rm) in Unix-like operating systems.

    Attributes:
        path (str): The builtin path to remove.

    **Examples:**

    .. code:: python

        yield Remove(path='/home/user/unwanted_file.txt')

    Usage:
        This class is designed to be used in a generator-based workflow where commands are yielded for execution.
    """

    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return f"Remove(path={self.path!r})"

    @staticmethod
    async def _remove_callback(host_info, global_info, command, cp, caller):
        """Static callback method for builtin removal"""

        # Validate host_info (matching Read_file error handling)
        required_keys = ['host', 'username', 'password']
        for key in required_keys:
            if key not in host_info or host_info[key] is None:
                raise ValueError(f"Missing or invalid value for '{key}' in host_info.")

        # Validate caller attributes (matching Read_file error handling)
        if caller.path is None:
            raise ValueError("The 'path' attribute of the caller cannot be None.")

        try:
            # Connect to the SSH server and remove the builtin
            async with asyncssh.connect(**host_info) as conn:
                async with conn.start_sftp_client() as sftp:
                    await reemote.gui.functions.remove.remove(path=caller.path)
        except (OSError, asyncssh.Error) as exc:
            raise  # Re-raise the exception to handle it in the caller

    def execute(self):
        r = yield Command(f"{self}", local=True, callback=self._remove_callback, caller=self)
        r.executed = True
        r.changed = False
        return r
