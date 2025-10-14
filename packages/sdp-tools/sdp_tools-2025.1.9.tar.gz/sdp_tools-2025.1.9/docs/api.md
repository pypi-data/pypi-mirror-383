# API Reference

Complete API documentation for sdp-tools modules.

## MinIO Module

### `minio_file` Class

```python
class minio_file(account: str)
```

Initialize a MinIO client for a specific account.

**Parameters:**
- `account` (str): Account identifier. Must be one of: `"WO"`, `"HO"`, `"ML"`, `"VIZ"`

**Raises:**
- `Exception`: If account is not one of the valid account names

**Environment Variables Required:**
- `MINIO_{ACCOUNT}_ACCESS_KEY`: MinIO access key
- `MINIO_{ACCOUNT}_SECRET_KEY`: MinIO secret key
- `MINIO_{ACCOUNT}_ENDPOINT`: MinIO endpoint URL (e.g., `https://minio.example.com`)
- `MINIO_{ACCOUNT}_BUCKET`: Target bucket name

**Example:**
```python
from minio_file import minio_file

# Initialize client for HO account
ho = minio_file("HO")
```

#### Methods

##### `get_buckets()`

Retrieve all available buckets from the MinIO server.

**Returns:**
- `list`: List of bucket objects with properties like `name` and `creation_date`

**Example:**
```python
buckets = ho.get_buckets()
for bucket in buckets:
    print(f"{bucket.name} - Created: {bucket.creation_date}")
```

##### `upload_file(file_name: str, full_name: str)`

Upload a file to MinIO.

**Parameters:**
- `file_name` (str): Path to the local file to upload
- `full_name` (str): Destination object name/path in MinIO

**Returns:**
- None

**Example:**
```python
# Upload local file to MinIO
ho.upload_file("data.csv", "datasets/2025/data.csv")
```

##### `download_file(file_name: str, full_name: str)`

Download a file from MinIO.

**Parameters:**
- `file_name` (str): Local path where the file will be saved
- `full_name` (str): Source object name/path in MinIO

**Returns:**
- None

**Example:**
```python
# Download file from MinIO to local path
ho.download_file("local_data.csv", "datasets/2025/data.csv")
```

##### `get_file_list()`

Print all objects in the configured bucket with their sizes.

**Returns:**
- None (prints to stdout)

**Output Format:**
```
object/path/file1.txt (1234 bytes)
object/path/file2.csv (5678 bytes)
```

**Example:**
```python
# List all files in the bucket
ho.get_file_list()
```

### Internal Methods

These methods are called automatically during initialization and are not typically called directly by users:

#### `_get_credentials()`

Retrieve credentials from environment variables for the configured account.

**Returns:**
- `dict`: Dictionary containing `bucket_name`, `access_key`, `secret_key`, and `endpoint`

#### `_get_client()`

Initialize the MinIO client using credentials from environment variables.

**Returns:**
- None (sets `self.client` and `self.bucket_name`)

---

## SURFdrive Module

### `download_surfdrive_csv(filename: str)`

Download a CSV file from SURFdrive public share and return as a pandas DataFrame.

**Parameters:**
- `filename` (str): Name of the file to download (currently unused in implementation, downloads from configured WebDAV endpoint)

**Returns:**
- `pandas.DataFrame` or `None`: DataFrame containing the CSV data, or None if download fails

**Environment Variables Required:**
- `SURFDRIVE_SHARE_TOKEN`: Public share token from SURFdrive
- `SURFDRIVE_PASSWORD`: Password for the public share

**HTTP Status Codes:**
- `200`: Success - CSV downloaded and parsed
- `401`: Unauthorized - Invalid credentials
- `404`: Not Found - File or share doesn't exist
- `500`: Server Error - SURFdrive server issue

**Example:**
```python
from surfdrive import download_surfdrive_csv

# Download CSV file
df = download_surfdrive_csv("data.csv")

if df is not None:
    print(f"Downloaded {len(df)} rows with {len(df.columns)} columns")
    print(df.head())
else:
    print("Download failed")
```

### `main()`

Command-line interface for downloading CSV files from SURFdrive.

**Command-line Arguments:**
- `sys.argv[1]`: Output filename for the downloaded CSV

**Environment Variables Required:**
- `SURFDRIVE_SHARE_TOKEN`
- `SURFDRIVE_PASSWORD`

**Example:**
```bash
# Set environment variables
export SURFDRIVE_SHARE_TOKEN="your-token"
export SURFDRIVE_PASSWORD="your-password"

# Run CLI
python -m surfdrive.surfdrive_download output.csv
```

**Behavior:**
- If no filename argument provided: Lists available objects (prints message and exits)
- If filename provided: Downloads CSV, prints preview, saves to specified file

### Constants

#### `SURFDRIVE_WEBDAV`

```python
SURFDRIVE_WEBDAV = "https://surfdrive.surf.nl/files/public.php/webdav"
```

The WebDAV endpoint URL for SURFdrive public shares.

---

## Type Hints

### MinIO Module

```python
from typing import List
from minio.datatypes import Bucket

class minio_file:
    account: str
    bucket_name: str
    client: Minio

    def __init__(self, account: str) -> None: ...
    def _get_credentials(self) -> dict[str, str]: ...
    def _get_client(self) -> None: ...
    def get_buckets(self) -> List[Bucket]: ...
    def upload_file(self, file_name: str, full_name: str) -> None: ...
    def download_file(self, file_name: str, full_name: str) -> None: ...
    def get_file_list(self) -> None: ...
```

### SURFdrive Module

```python
import pandas as pd
from typing import Optional

def download_surfdrive_csv(filename: str) -> Optional[pd.DataFrame]: ...
def main() -> None: ...
```

---

## Exception Handling

### MinIO Module

The `minio_file` class raises exceptions in the following cases:

```python
# Invalid account name
try:
    invalid = minio_file("INVALID")
except Exception as e:
    print(f"Error: {e}")  # "Incorrect account INVALID"

# Missing environment variables
# Will fail during initialization if credentials are not set

# MinIO client errors (network, authentication, etc.)
# Propagated from the underlying minio library
```

### SURFdrive Module

The `download_surfdrive_csv` function handles errors gracefully:

```python
# Returns None on HTTP errors (401, 404, 500, etc.)
df = download_surfdrive_csv("data.csv")
if df is None:
    print("Download failed - check logs for HTTP status code")

# Raises exceptions for network errors
try:
    df = download_surfdrive_csv("data.csv")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Connection failed")
```

---

## Complete Usage Example

```python
import os
from minio_file import minio_file
from surfdrive import download_surfdrive_csv
import tempfile

# Set up environment
os.environ['MINIO_ML_ACCESS_KEY'] = 'your-key'
os.environ['MINIO_ML_SECRET_KEY'] = 'your-secret'
os.environ['MINIO_ML_ENDPOINT'] = 'https://minio.example.com'
os.environ['MINIO_ML_BUCKET'] = 'ml-datasets'

os.environ['SURFDRIVE_SHARE_TOKEN'] = 'share-token'
os.environ['SURFDRIVE_PASSWORD'] = 'share-password'

# Download from SURFdrive
print("Downloading from SURFdrive...")
df = download_surfdrive_csv("input_data.csv")

if df is not None:
    print(f"Downloaded {len(df)} rows")

    # Process data
    df['processed'] = df['value'] * 2

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        # Upload to MinIO
        print("Uploading to MinIO...")
        ml = minio_file("ML")
        ml.upload_file(tmp_path, "processed/output_data.csv")

        # Verify upload
        print("\nVerifying upload...")
        ml.get_file_list()

        print("\nSuccess!")
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
else:
    print("Download failed")
```