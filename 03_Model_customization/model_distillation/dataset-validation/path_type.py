from enum import Enum


class PathType(Enum):
    """Enum for path types."""
    FILE = "file"
    FOLDER = "folder"
    S3 = "s3"
