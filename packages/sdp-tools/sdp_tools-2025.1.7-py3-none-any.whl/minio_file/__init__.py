"""MinIO File management tool."""

__version__ = "2025.1.7"

# Legacy class-based API (for backward compatibility)
# Functional API (recommended)
from .minio_file import (
    MinioConnection,
    create_connection,
    download_file,
    get_buckets,
    list_files,
    main,
    minio_file,
    upload_file,
)

__all__ = [
    # Functional API
    "MinioConnection",
    "create_connection",
    "upload_file",
    "download_file",
    "list_files",
    "get_buckets",
    # Legacy
    "minio_file",
    "main",
]
