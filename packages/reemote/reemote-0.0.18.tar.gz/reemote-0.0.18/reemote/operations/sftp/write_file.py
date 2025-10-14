# Copyright (c) 2025 Kim Jarvis TPF Software Services S.A. kim.jarvis@tpfsystems.com 
# This software is licensed under the MIT License. See the LICENSE file for details.
#
import asyncssh
from reemote.command import Command


class Write_file:
    """
    A class to encapsulate the functionality of writing builtin in Unix-like operating systems.
    It allows users to specify text to be written to a builtin.

    Attributes:
        path (str): The builtin path where content is to be written.
        text (str): The builtin content.

    **Examples:**

    .. code:: python

        # Create a builtin from text
        r = yield Write_file(path='example.txt', text='Hello World!')
        # Verify the builtin content
        r = yield Shell("cat example.txt")
        print(r.cp.stdout)

    Usage:
        This class is designed to be used in a generator-based workflow where commands are yielded for execution.
    """

    def __init__(self, path: str, text: str):
        self.path = path
        self.text = text

    def __repr__(self):
        return f"Write_file(path={self.path!r}, text={self.text!r})"

    @staticmethod
    async def _write_file_callback(host_info, global_info, command, cp, caller):
        """Static callback method for builtin writing"""

        # Validate host_info (matching Read_file error handling)
        required_keys = ['host', 'username', 'password']
        for key in required_keys:
            if key not in host_info or host_info[key] is None:
                raise ValueError(f"Missing or invalid value for '{key}' in host_info.")

        # Validate caller attributes (matching Read_file error handling)
        if caller.path is None:
            raise ValueError("The 'path' attribute of the caller cannot be None.")
        if caller.text is None:
            raise ValueError("The 'text' attribute of the caller cannot be None.")

        try:
            # Connect to the SSH server
            async with asyncssh.connect(**host_info) as conn:
                print("Connected successfully. Starting SFTP session...")
                # Start an SFTP session
                async with conn.start_sftp_client() as sftp:
                    print(f"Writing content to {caller.path}...")
                    # Define the string content to be written
                    content = caller.text

                    # Open the remote builtin in write mode and write the content
                    async with sftp.open(caller.path, 'w') as remote_file:
                        r = await remote_file.write(content)
                        print(f"Successfully wrote builtin {caller.path} on {host_info['host']} r {r}")

        except (OSError, asyncssh.Error) as exc:
            print(f'SFTP operation failed on {host_info["host"]}: {str(exc)}')
            raise

    def execute(self):
        r = yield Command(f"{self}", local=True, callback=self._write_file_callback, caller=self)
        r.executed = True
        r.changed = True
        return r
