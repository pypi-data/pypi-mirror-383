#!/usr/bin/env python3
"""Example usage of the functional MinIO API.

This demonstrates the new functional interface for MinIO operations.
"""

from minio_file import create_connection, download_file, get_buckets, list_files, upload_file

# Example 1: Using account-based connection (reads from environment variables)
# Set these environment variables first:
#   MINIO_HO_ENDPOINT=https://minio.example.com
#   MINIO_HO_ACCESS_KEY=your-access-key
#   MINIO_HO_SECRET_KEY=your-secret-key
#   MINIO_HO_BUCKET=your-bucket

conn = create_connection(account="HO")

# Upload a file
upload_file(conn, local_path="data.csv", remote_path="uploads/data.csv")

# Download a file
download_file(conn, remote_path="uploads/data.csv", local_path="downloaded.csv")

# List all files
files = list_files(conn)
for file in files:
    print(f"{file['object_name']} - {file['size']} bytes")

# List files with prefix
uploads = list_files(conn, prefix="uploads/")
print(f"Found {len(uploads)} files in uploads/")

# Get all buckets
buckets = get_buckets(conn)
print(f"Available buckets: {buckets}")

# Example 2: Using explicit credentials
conn2 = create_connection(
    endpoint="https://minio.example.com",
    access_key="my-access-key",
    secret_key="my-secret-key",
    bucket="my-bucket",
)

# Use the connection for operations
upload_file(conn2, "local.txt", "remote.txt")

# Example 3: Override bucket for specific operations
upload_file(conn, "file.txt", "backup/file.txt", bucket="backup-bucket")

print("✅ All operations completed successfully!")
