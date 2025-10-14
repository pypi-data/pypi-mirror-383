# Usage Guide

This guide provides detailed examples for using sdp-tools' two main modules: MinIO file management and SURFdrive downloads.

## MinIO File Management

### Multi-Account Support

The MinIO module supports four different accounts: WO, HO, ML, and VIZ. Each account has its own set of credentials configured via environment variables.

### Setup

First, configure environment variables for your account:

```bash
# For HO account
export MINIO_HO_ACCESS_KEY="your-access-key"
export MINIO_HO_SECRET_KEY="your-secret-key"
export MINIO_HO_ENDPOINT="https://minio.example.com"
export MINIO_HO_BUCKET="your-bucket-name"
```

### Basic Operations

#### Initialize Client

```python
from minio_file import minio_file

# Create client for specific account
ho = minio_file("HO")
```

#### Upload Files

```python
# Upload a single file
ho.upload_file("local_file.txt", "remote/path/file.txt")

# Upload with different remote name
ho.upload_file("data.csv", "datasets/2025/january/data.csv")
```

#### Download Files

```python
# Download a file
ho.download_file("downloaded_file.txt", "remote/path/file.txt")

# Download to specific local path
ho.download_file("/tmp/data.csv", "datasets/2025/january/data.csv")
```

#### List Files

```python
# List all files in the bucket
ho.get_file_list()

# Output will show:
# remote/path/file.txt (1234 bytes)
# datasets/2025/january/data.csv (5678 bytes)
```

#### Manage Buckets

```python
# Get all available buckets
buckets = ho.get_buckets()
for bucket in buckets:
    print(f"Bucket: {bucket.name}, Created: {bucket.creation_date}")
```

### Working with Multiple Accounts

```python
from minio_file import minio_file

# Connect to different accounts
ho = minio_file("HO")
ml = minio_file("ML")

# Upload to HO account
ho.upload_file("data.csv", "inputs/data.csv")

# Download from ML account
ml.download_file("model.pkl", "models/latest/model.pkl")
```

### Error Handling

```python
from minio_file import minio_file

try:
    ho = minio_file("HO")
    ho.upload_file("data.csv", "remote/data.csv")
    print("Upload successful!")
except Exception as e:
    print(f"Error: {e}")
```

## SURFdrive Integration

### Setup

Configure SURFdrive credentials:

```bash
export SURFDRIVE_SHARE_TOKEN="your-share-token"
export SURFDRIVE_PASSWORD="your-password"
```

### Basic CSV Download

```python
from surfdrive import download_surfdrive_csv

# Download CSV file
df = download_surfdrive_csv("data.csv")

if df is not None:
    print(f"Successfully downloaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head())
else:
    print("Download failed")
```

### Working with Downloaded Data

```python
from surfdrive import download_surfdrive_csv
import pandas as pd

# Download and process
df = download_surfdrive_csv("sales_data.csv")

if df is not None:
    # Basic statistics
    print(df.describe())

    # Filter data
    recent = df[df['date'] > '2024-01-01']

    # Save locally
    df.to_csv("local_copy.csv", index=False)

    # Save as parquet for better performance
    df.to_parquet("local_copy.parquet", index=False)
```

### CLI Usage

```bash
# Download using command line
python -m surfdrive.surfdrive_download output.csv
```

### Error Handling

```python
from surfdrive import download_surfdrive_csv
import sys

try:
    df = download_surfdrive_csv("data.csv")

    if df is None:
        print("Download failed - check credentials and share URL")
        sys.exit(1)

    print(f"Success! Downloaded {len(df)} rows")

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
```

## Combined Workflow

Transfer data from SURFdrive to MinIO:

```python
from surfdrive import download_surfdrive_csv
from minio_file import minio_file
import tempfile

# Download from SURFdrive
print("Downloading from SURFdrive...")
df = download_surfdrive_csv("input_data.csv")

if df is not None:
    print(f"Downloaded {len(df)} rows")

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name

    # Upload to MinIO
    print("Uploading to MinIO...")
    ml = minio_file("ML")
    ml.upload_file(tmp_path, "datasets/surfdrive_data.csv")

    print("Transfer complete!")
else:
    print("Download failed")
```

## Advanced Usage

### Batch Operations

```python
from minio_file import minio_file
import os

ho = minio_file("HO")

# Upload multiple files
local_dir = "/path/to/files"
remote_prefix = "batch_upload"

for filename in os.listdir(local_dir):
    if filename.endswith('.csv'):
        local_path = os.path.join(local_dir, filename)
        remote_path = f"{remote_prefix}/{filename}"

        print(f"Uploading {filename}...")
        ho.upload_file(local_path, remote_path)

print("Batch upload complete!")
```

### Verification

```python
from minio_file import minio_file
import os

ho = minio_file("HO")

# Upload file
local_file = "important_data.csv"
remote_file = "data/important_data.csv"

ho.upload_file(local_file, remote_file)

# Verify by listing
print("Verifying upload...")
ho.get_file_list()

# Could also download and compare
ho.download_file("verify_download.csv", remote_file)

# Compare files
import filecmp
if filecmp.cmp(local_file, "verify_download.csv"):
    print("✓ Upload verified successfully!")
else:
    print("✗ Files don't match!")
```

## Best Practices

### 1. Environment Variable Management

Use `.env` files for local development:

```bash
# .env file
MINIO_HO_ACCESS_KEY=your-key
MINIO_HO_SECRET_KEY=your-secret
MINIO_HO_ENDPOINT=https://minio.example.com
MINIO_HO_BUCKET=my-bucket

SURFDRIVE_SHARE_TOKEN=token123
SURFDRIVE_PASSWORD=pass456
```

Load with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

from minio_file import minio_file
ho = minio_file("HO")
```

### 2. Error Handling

Always wrap operations in try-except blocks:

```python
try:
    ho = minio_file("HO")
    ho.upload_file("data.csv", "remote.csv")
except ValueError as e:
    print(f"Invalid account or configuration: {e}")
except Exception as e:
    print(f"Upload failed: {e}")
```

### 3. Resource Cleanup

```python
import tempfile
import os

# Use context managers for temporary files
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
    df.to_csv(tmp.name, index=False)
    tmp_path = tmp.name

try:
    ho.upload_file(tmp_path, "remote.csv")
finally:
    # Clean up temporary file
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
```

### 4. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting upload...")
    ho = minio_file("HO")
    ho.upload_file("data.csv", "remote.csv")
    logger.info("Upload complete")
except Exception as e:
    logger.error(f"Upload failed: {e}")
```