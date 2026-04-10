import os
import gzip
from constants import MAX_SIZE


class FileUtils:
    @staticmethod
    def validate_file_size(file_path, is_invocation_logs):
        """Validate that the file size does not exceed max size."""
        if is_invocation_logs:
            return True
        file_size = os.path.getsize(file_path)
        if file_size > MAX_SIZE:
            return False
        return True

    @staticmethod
    def open_file(file_path, is_invocation_logs):
        """Read a file and return its content."""
        if is_invocation_logs:
            return gzip.open(file_path, "r")
        else:
            return open(file_path, "r")

    @staticmethod
    def convert_bytes_to_Gb(size_in_bytes):
        """Convert bytes to gigabytes."""
        return size_in_bytes / 1024 / 1024 / 1024
