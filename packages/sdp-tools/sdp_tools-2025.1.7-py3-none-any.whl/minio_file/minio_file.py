#!/usr/bin/env python3
"""MinIO File Operations with Functional API

Provides functional interface for MinIO operations with connection handlers.
Supports both environment variable-based and explicit credential configuration.
"""

from os import getenv
from pathlib import Path
from sys import argv
from typing import Any, Dict, List, Optional

import urllib3
from minio import Minio

# Disable SSL warnings if using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MinioConnection:
    """Connection handler for MinIO operations.

    This class encapsulates the MinIO client and bucket configuration.
    Use create_connection() to create instances.
    """

    def __init__(self, client: Minio, bucket_name: str):
        """Initialize connection handler.

        Args:
            client: MinIO client instance
            bucket_name: Default bucket name for operations
        """
        self.client = client
        self.bucket_name = bucket_name


def create_connection(
    account: Optional[str] = None,
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
    secure: Optional[bool] = None,
) -> MinioConnection:
    """Create a MinIO connection handler.

    Can be used in two modes:
    1. Account-based (reads from environment variables):
       conn = create_connection(account="HO")

    2. Explicit credentials:
       conn = create_connection(
           endpoint="https://minio.example.com",
           access_key="your-key",
           secret_key="your-secret",
           bucket="your-bucket"
       )

    Args:
        account: Account identifier (WO, HO, ML, VIZ). Reads credentials from env vars.
        endpoint: MinIO endpoint URL (e.g., "https://minio.example.com")
        access_key: MinIO access key
        secret_key: MinIO secret key
        bucket: Bucket name
        secure: Use HTTPS (auto-detected from endpoint if not specified)

    Returns:
        MinioConnection: Connection handler for MinIO operations

    Raises:
        ValueError: If account is invalid or required credentials are missing

    Examples:
        >>> # Using account (env vars)
        >>> conn = create_connection(account="HO")

        >>> # Using explicit credentials
        >>> conn = create_connection(
        ...     endpoint="https://minio.example.com",
        ...     access_key="mykey",
        ...     secret_key="mysecret",
        ...     bucket="mybucket"
        ... )
    """
    if account is not None:
        # Account-based mode: read from environment variables
        if account not in ["WO", "HO", "ML", "VIZ"]:
            raise ValueError(f"Invalid account '{account}'. Must be one of: WO, HO, ML, VIZ")

        endpoint = getenv(f"MINIO_{account}_ENDPOINT")
        access_key = getenv(f"MINIO_{account}_ACCESS_KEY")
        secret_key = getenv(f"MINIO_{account}_SECRET_KEY")
        bucket = getenv(f"MINIO_{account}_BUCKET")

        if not all([endpoint, access_key, secret_key, bucket]):
            missing = []
            if not endpoint:
                missing.append(f"MINIO_{account}_ENDPOINT")
            if not access_key:
                missing.append(f"MINIO_{account}_ACCESS_KEY")
            if not secret_key:
                missing.append(f"MINIO_{account}_SECRET_KEY")
            if not bucket:
                missing.append(f"MINIO_{account}_BUCKET")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    else:
        # Explicit credentials mode
        if not all([endpoint, access_key, secret_key, bucket]):
            raise ValueError("When not using account, you must provide: endpoint, access_key, secret_key, and bucket")

    # Parse endpoint and determine security
    endpoint_url = endpoint.replace("http://", "").replace("https://", "")
    if secure is None:
        secure = endpoint.startswith("https://")

    # Create MinIO client
    client = Minio(
        endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )

    return MinioConnection(client=client, bucket_name=bucket)


def upload_file(conn: MinioConnection, local_path: str, remote_path: str, bucket: Optional[str] = None) -> None:
    """Upload a file to MinIO.

    Args:
        conn: MinIO connection handler
        local_path: Path to local file
        remote_path: Destination path in MinIO bucket
        bucket: Override default bucket (optional)

    Examples:
        >>> conn = create_connection(account="HO")
        >>> upload_file(conn, "data.csv", "uploads/data.csv")
    """
    bucket_name = bucket or conn.bucket_name
    conn.client.fput_object(bucket_name=bucket_name, file_path=local_path, object_name=remote_path)


def download_file(conn: MinioConnection, remote_path: str, local_path: str, bucket: Optional[str] = None) -> None:
    """Download a file from MinIO.

    Args:
        conn: MinIO connection handler
        remote_path: Path to file in MinIO bucket
        local_path: Destination path for downloaded file
        bucket: Override default bucket (optional)

    Examples:
        >>> conn = create_connection(account="HO")
        >>> download_file(conn, "uploads/data.csv", "data.csv")
    """
    bucket_name = bucket or conn.bucket_name
    conn.client.fget_object(bucket_name=bucket_name, object_name=remote_path, file_path=local_path)


def list_files(
    conn: MinioConnection, bucket: Optional[str] = None, prefix: str = "", recursive: bool = True
) -> List[Dict[str, Any]]:
    """List files in MinIO bucket.

    Args:
        conn: MinIO connection handler
        bucket: Override default bucket (optional)
        prefix: Filter results by prefix (optional)
        recursive: List recursively (default: True)

    Returns:
        List of dictionaries with file information (object_name, size, last_modified)

    Examples:
        >>> conn = create_connection(account="HO")
        >>> files = list_files(conn)
        >>> for file in files:
        ...     print(f"{file['object_name']} ({file['size']} bytes)")
    """
    bucket_name = bucket or conn.bucket_name
    objects = conn.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)

    result = []
    for obj in objects:
        result.append(
            {
                "object_name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "etag": obj.etag,
            }
        )
    return result


def get_buckets(conn: MinioConnection) -> List[str]:
    """Get list of all available buckets.

    Args:
        conn: MinIO connection handler

    Returns:
        List of bucket names

    Examples:
        >>> conn = create_connection(account="HO")
        >>> buckets = get_buckets(conn)
        >>> print(buckets)
        ['bucket1', 'bucket2']
    """
    return [bucket.name for bucket in conn.client.list_buckets()]


# Legacy class-based API for backward compatibility
class minio_file:
    """Legacy class-based API (deprecated, use functional API instead).

    This class is maintained for backward compatibility.
    New code should use the functional API:
        conn = create_connection(account="HO")
        upload_file(conn, "local.txt", "remote.txt")
    """

    def __init__(self, account: str):
        """Initialize MinIO client for specified account.

        Args:
            account: Account identifier (WO, HO, ML, VIZ)
        """
        self._conn = create_connection(account=account)

    def get_buckets(self) -> List[Any]:
        """Retrieve all the buckets available."""
        return list(self._conn.client.list_buckets())

    def upload_file(self, file_name: str, full_name: str) -> None:
        """Upload a file."""
        upload_file(self._conn, file_name, full_name)

    def get_file_list(self) -> None:
        """Retrieve all files in the bucket."""
        files = list_files(self._conn)
        for file_info in files:
            print(f"{file_info['object_name']} ({file_info['size']} bytes)")

    def download_file(self, file_name: str, full_name: str) -> None:
        """Download a file."""
        download_file(self._conn, full_name, file_name)


def main():
    """Main function (for CLI)"""
    ho = minio_file("HO")
    # Handle commanod line arguments
    if len(argv) == 3:
        ho_file = argv[1]
        ho_obj = Path(ho_file)
        # ml_file = argv[2]
        # ml_obj = Path(ml_file)

        if ho_obj.is_file():
            print(f"Skipping existing file: {ho_obj}")
        else:
            ho.download_file(ho_file, str(ho_obj))
    else:
        # List uploaded objects
        print("\nListing objects in bucket:")
        ho.get_file_list()


if __name__ == "__main__":
    main()
