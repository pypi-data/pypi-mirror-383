# Copyright (c) 2025 Kim Jarvis TPF Software Services S.A. kim.jarvis@tpfsystems.com 
# This software is licensed under the MIT License. See the LICENSE file for details.
#
class Multi_file_transfer_progress:
    """
    Progress handler that tracks multiple builtin

    Args:
        src_path: Source builtin path
        dst_path: Destination builtin path
        copied_bytes: Number of bytes copied so far
        total_bytes: Total bytes to copy (None if unknown)
    """

    def __init__(self):
        self.files = {}
        self.start_time = time.time()

    def __call__(self, src_path, dst_path, copied_bytes, total_bytes):
        # Track current builtin progress
        self.files[src_path] = (copied_bytes, total_bytes)

        # Calculate overall progress
        total_files = len(self.files)
        completed_files = sum(1 for copied, total in self.files.values()
                              if total and copied == total)

        elapsed = time.time() - self.start_time
        print(f"Files: {completed_files}/{total_files} completed | Time: {elapsed:.1f}s")

        # Show current builtin progress
        if total_bytes:
            percentage = (copied_bytes / total_bytes) * 100
            print(f"Current: {os.path.basename(src_path)} - {percentage:.1f}%")

