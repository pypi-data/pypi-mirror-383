# Functional API Guide

The MinIO module now provides a modern functional API alongside the legacy class-based API. The functional API offers better composability, testability, and follows modern Python best practices.

## Table of Contents

- [Why Functional API?](#why-functional-api)
- [Quick Start](#quick-start)
- [Creating Connections](#creating-connections)
- [File Operations](#file-operations)
- [Bucket Operations](#bucket-operations)
- [Advanced Usage](#advanced-usage)
- [Migration Guide](#migration-guide)

## Why Functional API?

The new functional API provides several advantages:

1. **Separation of Concerns**: Connection creation is separate from operations
2. **Flexibility**: Pass connections to different functions easily
3. **Testability**: Easier to mock and test individual operations
4. **Composability**: Build complex workflows by combining simple functions
5. **Type Safety**: Full type hints for better IDE support and type checking

## Quick Start

```python
from minio_file import create_connection, upload_file, download_file, list_files

# Create a connection
conn = create_connection(account="HO")

# Use the connection for operations
upload_file(conn, "local.csv", "remote/path/data.csv")
download_file(conn, "remote/path/data.csv", "local_copy.csv")

# List files
files = list_files(conn)
for file in files:
    print(f"{file['object_name']} ({file['size']} bytes)")
```

## Creating Connections

### Account-Based Connection

Use environment variables with account naming:

```python
from minio_file import create_connection

# Reads from MINIO_HO_* environment variables
conn = create_connection(account="HO")
```

**Required environment variables:**
- `MINIO_HO_ENDPOINT` - MinIO server URL
- `MINIO_HO_ACCESS_KEY` - Access key
- `MINIO_HO_SECRET_KEY` - Secret key
- `MINIO_HO_BUCKET` - Default bucket name

**Supported accounts:** `WO`, `HO`, `ML`, `VIZ`

### Explicit Credentials

Provide credentials directly:

```python
from minio_file import create_connection

conn = create_connection(
    endpoint="https://minio.example.com",
    access_key="your-access-key",
    secret_key="your-secret-key",
    bucket="your-bucket"
)
```

### Advanced Options

```python
# Force HTTP instead of HTTPS
conn = create_connection(
    endpoint="http://localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket="test-bucket",
    secure=False  # Explicitly use HTTP
)
```

## File Operations

### Upload Files

```python
from minio_file import create_connection, upload_file

conn = create_connection(account="HO")

# Basic upload
upload_file(conn, local_path="data.csv", remote_path="uploads/data.csv")

# Upload to different bucket
upload_file(conn, local_path="backup.zip", remote_path="backups/backup.zip", bucket="backup-bucket")
```

### Download Files

```python
from minio_file import create_connection, download_file

conn = create_connection(account="HO")

# Basic download
download_file(conn, remote_path="uploads/data.csv", local_path="data.csv")

# Download from different bucket
download_file(conn, remote_path="file.txt", local_path="file.txt", bucket="other-bucket")
```

### List Files

```python
from minio_file import create_connection, list_files

conn = create_connection(account="HO")

# List all files
files = list_files(conn)
for file in files:
    print(f"Name: {file['object_name']}")
    print(f"Size: {file['size']} bytes")
    print(f"Modified: {file['last_modified']}")
    print(f"ETag: {file['etag']}")
    print()

# List files with prefix
uploads = list_files(conn, prefix="uploads/")
print(f"Found {len(uploads)} files in uploads/")

# Non-recursive listing
top_level = list_files(conn, recursive=False)
```

## Bucket Operations

### Get All Buckets

```python
from minio_file import create_connection, get_buckets

conn = create_connection(account="HO")

buckets = get_buckets(conn)
print(f"Available buckets: {buckets}")
# Output: ['bucket1', 'bucket2', 'bucket3']
```

## Advanced Usage

### Multiple Connections

```python
from minio_file import create_connection, upload_file, download_file

# Create multiple connections
ho_conn = create_connection(account="HO")
ml_conn = create_connection(account="ML")

# Use different connections for different operations
download_file(ho_conn, "source/data.csv", "temp.csv")
upload_file(ml_conn, "temp.csv", "ml/data.csv")
```

### Error Handling

```python
from minio_file import create_connection, upload_file

try:
    conn = create_connection(account="HO")
    upload_file(conn, "data.csv", "uploads/data.csv")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Upload failed: {e}")
```

### Using with Context Managers

```python
from minio_file import create_connection, list_files

def backup_files(account: str, backup_bucket: str):
    """Backup all files from one bucket to another."""
    conn = create_connection(account=account)

    files = list_files(conn)
    for file in files:
        download_file(conn, file['object_name'], f"/tmp/{file['object_name']}")
        upload_file(conn, f"/tmp/{file['object_name']}", file['object_name'], bucket=backup_bucket)

    return len(files)

# Use the function
num_backed_up = backup_files("HO", "backup-bucket")
print(f"Backed up {num_backed_up} files")
```

### Filtering and Processing

```python
from minio_file import create_connection, list_files
from datetime import datetime, timedelta

conn = create_connection(account="HO")

# Get files modified in last 7 days
week_ago = datetime.now() - timedelta(days=7)
recent_files = [
    f for f in list_files(conn)
    if f['last_modified'] > week_ago
]

# Get CSV files only
csv_files = list_files(conn, prefix="data/")
csv_files = [f for f in csv_files if f['object_name'].endswith('.csv')]

print(f"Found {len(csv_files)} CSV files")
```

## Migration Guide

### From Class-Based to Functional API

**Old class-based API:**
```python
from minio_file import minio_file

ho = minio_file("HO")
ho.upload_file("local.txt", "remote.txt")
ho.download_file("local.txt", "remote.txt")
ho.get_file_list()
buckets = ho.get_buckets()
```

**New functional API:**
```python
from minio_file import create_connection, upload_file, download_file, list_files, get_buckets

conn = create_connection(account="HO")
upload_file(conn, "local.txt", "remote.txt")
download_file(conn, "remote.txt", "local.txt")
files = list_files(conn)
for f in files:
    print(f"{f['object_name']} ({f['size']} bytes)")
buckets = get_buckets(conn)
```

**Key differences:**

1. **Connection Creation**: Use `create_connection()` instead of `minio_file(account)`
2. **Parameter Order**:
   - Old: `download_file(local_path, remote_path)`
   - New: `download_file(conn, remote_path, local_path)` (remote first, more intuitive)
3. **List Files**: Returns list of dicts instead of printing (more flexible)
4. **Get Buckets**: Returns list of strings instead of list of bucket objects

### Backward Compatibility

The old class-based API still works and will continue to be supported:

```python
# This still works!
from minio_file import minio_file

ho = minio_file("HO")
ho.upload_file("file.txt", "remote/file.txt")
```

However, we recommend migrating to the functional API for new code.

## API Reference

### `create_connection()`

```python
def create_connection(
    account: Optional[str] = None,
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
    secure: Optional[bool] = None,
) -> MinioConnection
```

**Parameters:**
- `account`: Account identifier (WO, HO, ML, VIZ)
- `endpoint`: MinIO endpoint URL
- `access_key`: Access key
- `secret_key`: Secret key
- `bucket`: Default bucket name
- `secure`: Use HTTPS (auto-detected if not specified)

**Returns:** `MinioConnection` object

**Raises:** `ValueError` if credentials are invalid or missing

### `upload_file()`

```python
def upload_file(
    conn: MinioConnection,
    local_path: str,
    remote_path: str,
    bucket: Optional[str] = None
) -> None
```

**Parameters:**
- `conn`: Connection handler
- `local_path`: Path to local file
- `remote_path`: Destination path in MinIO
- `bucket`: Override default bucket (optional)

### `download_file()`

```python
def download_file(
    conn: MinioConnection,
    remote_path: str,
    local_path: str,
    bucket: Optional[str] = None
) -> None
```

**Parameters:**
- `conn`: Connection handler
- `remote_path`: Path to file in MinIO
- `local_path`: Destination path for download
- `bucket`: Override default bucket (optional)

### `list_files()`

```python
def list_files(
    conn: MinioConnection,
    bucket: Optional[str] = None,
    prefix: str = "",
    recursive: bool = True
) -> List[Dict[str, Any]]
```

**Parameters:**
- `conn`: Connection handler
- `bucket`: Override default bucket (optional)
- `prefix`: Filter by prefix (optional)
- `recursive`: List recursively (default: True)

**Returns:** List of dictionaries with keys: `object_name`, `size`, `last_modified`, `etag`

### `get_buckets()`

```python
def get_buckets(conn: MinioConnection) -> List[str]
```

**Parameters:**
- `conn`: Connection handler

**Returns:** List of bucket names

## Best Practices

1. **Reuse Connections**: Create one connection and pass it to multiple operations
2. **Handle Errors**: Always wrap operations in try-except blocks
3. **Use Type Hints**: Leverage type hints for better IDE support
4. **Check File Sizes**: Use `list_files()` to check sizes before downloading
5. **Use Prefixes**: Filter files efficiently with the `prefix` parameter
6. **Environment Variables**: Use account-based connections with environment variables for security

## Examples

See the [examples directory](../examples/) for complete working examples:

- `functional_api_example.py` - Basic usage of the functional API
- More examples coming soon!

## Support

For issues and questions:
- GitHub Issues: https://github.com/cedanl/sdp-tools/issues
- Documentation: https://github.com/cedanl/sdp-tools/tree/main/docs
