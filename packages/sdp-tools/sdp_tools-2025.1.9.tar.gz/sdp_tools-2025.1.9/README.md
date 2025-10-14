# SDP Tools

A Python toolkit for Scientific Data Platform operations, providing utilities for MinIO object storage and SURFdrive file transfers.

## Features

### MinIO File Management
- 🔐 Multi-account configuration support (WO, HO, ML, VIZ)
- 📁 Upload and download files
- 🪣 Bucket management and listing
- 🔍 List and verify uploaded objects
- ⚡ Environment-based credential management

### SURFdrive Integration
- 📥 Download CSV files from SURFdrive public shares
- 🔒 HTTP Basic Authentication support
- 📊 Direct pandas DataFrame integration
- 🌐 WebDAV protocol support

## Installation

### From PyPI (coming soon)
```bash
pip install sdp-tools
```

### From source
```bash
# Clone the repository
git clone https://github.com/cedanl/sdp-tools
cd sdp-tools

# Install with uv (recommended)
uv pip install -e ".[dev,test]"

# Or with pip
pip install -e ".[dev,test]"
```

## Quick Start

### MinIO File Operations

The MinIO module supports multiple accounts through environment variable naming patterns.

#### Configuration

Set environment variables for your account (replace `{ACCOUNT}` with WO, HO, ML, or VIZ):

```bash
export MINIO_HO_ACCESS_KEY="your-access-key"
export MINIO_HO_SECRET_KEY="your-secret-key"
export MINIO_HO_ENDPOINT="https://minio.example.com"
export MINIO_HO_BUCKET="your-bucket-name"
```

#### Usage

```python
from minio_file import minio_file

# Initialize client for specific account
ho = minio_file("HO")

# Upload a file
ho.upload_file("local_file.txt", "remote/path/file.txt")

# Download a file
ho.download_file("local_download.txt", "remote/path/file.txt")

# List all files in bucket
ho.get_file_list()

# Get all available buckets
buckets = ho.get_buckets()
for bucket in buckets:
    print(bucket.name)
```

### SURFdrive File Downloads

Download CSV files from SURFdrive public shares directly into pandas DataFrames.

#### Configuration

```bash
export SURFDRIVE_SHARE_TOKEN="your-share-token"
export SURFDRIVE_PASSWORD="your-password"
```

#### Usage

```python
from surfdrive import download_surfdrive_csv

# Download CSV and get DataFrame
df = download_surfdrive_csv("data.csv")

if df is not None:
    print(f"Downloaded {len(df)} rows")
    print(df.head())

    # Save locally if needed
    df.to_csv("local_copy.csv", index=False)
```

Or use the CLI:

```bash
# Set environment variables first
export SURFDRIVE_SHARE_TOKEN="your-token"
export SURFDRIVE_PASSWORD="your-password"

# Download and save CSV
python -m surfdrive.surfdrive_download output.csv
```

## Environment Variables

### MinIO Configuration

Each account uses a prefix pattern: `MINIO_{ACCOUNT}_*`

| Variable Pattern | Required | Description | Accounts |
|----------|----------|-------------|----------|
| `MINIO_{ACCOUNT}_ACCESS_KEY` | ✅ | MinIO access key | WO, HO, ML, VIZ |
| `MINIO_{ACCOUNT}_SECRET_KEY` | ✅ | MinIO secret key | WO, HO, ML, VIZ |
| `MINIO_{ACCOUNT}_ENDPOINT` | ✅ | MinIO endpoint URL | WO, HO, ML, VIZ |
| `MINIO_{ACCOUNT}_BUCKET` | ✅ | Target bucket name | WO, HO, ML, VIZ |

**Example for HO account:**
- `MINIO_HO_ACCESS_KEY`
- `MINIO_HO_SECRET_KEY`
- `MINIO_HO_ENDPOINT`
- `MINIO_HO_BUCKET`

### SURFdrive Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `SURFDRIVE_SHARE_TOKEN` | ✅ | Public share token from SURFdrive |
| `SURFDRIVE_PASSWORD` | ✅ | Password for the public share |

## Development

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Or manually
uv pip install -e ".[dev,test]"
```

### Running Tests

```bash
# Run all fast tests
make test-fast

# Run all tests including slow ones
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_surfdrive.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Run all checks (lint + tests)
make check
```

### Building

```bash
# Build package
make build

# Build and verify
make build-check
```

## Project Structure

```
sdp-tools/
├── src/
│   ├── minio_file/          # MinIO operations module
│   │   ├── __init__.py
│   │   └── minio_file.py
│   └── surfdrive/           # SURFdrive operations module
│       ├── __init__.py
│       └── surfdrive_download.py
├── tests/                   # Test suite
│   ├── test_imports.py
│   ├── test_functionality.py
│   ├── test_surfdrive.py
│   └── test_and_build_distribution.py
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
├── Makefile                # Development commands
└── README.md               # This file
```

## API Reference

### MinIO Module (`minio_file`)

#### Class: `minio_file(account)`

Initialize a MinIO client for a specific account.

**Parameters:**
- `account` (str): Account identifier. Must be one of: "WO", "HO", "ML", "VIZ"

**Methods:**

- `get_buckets()` → list: Retrieve all available buckets
- `upload_file(file_name, full_name)`: Upload a file to MinIO
  - `file_name`: Local file path
  - `full_name`: Remote object path
- `download_file(file_name, full_name)`: Download a file from MinIO
  - `file_name`: Local destination path
  - `full_name`: Remote object path
- `get_file_list()`: Print all objects in the bucket

**Example:**
```python
from minio_file import minio_file

# Initialize for ML account
ml = minio_file("ML")

# Upload
ml.upload_file("data.csv", "datasets/data.csv")

# Download
ml.download_file("local_data.csv", "datasets/data.csv")
```

### SURFdrive Module (`surfdrive`)

#### Function: `download_surfdrive_csv(filename)`

Download a CSV file from SURFdrive public share.

**Parameters:**
- `filename` (str): Name of the file to download (currently unused, downloads from configured share)

**Returns:**
- `pandas.DataFrame` or `None`: DataFrame with CSV data, or None if download fails

**Environment Variables Required:**
- `SURFDRIVE_SHARE_TOKEN`
- `SURFDRIVE_PASSWORD`

**Example:**
```python
from surfdrive import download_surfdrive_csv

df = download_surfdrive_csv("data.csv")
if df is not None:
    print(f"Shape: {df.shape}")
    print(df.describe())
```

## Troubleshooting

### MinIO Issues

#### Invalid Account Error
```
Incorrect account {account}
```
**Solution:** Use only valid account names: "WO", "HO", "ML", or "VIZ"

#### Missing Environment Variables
```
Missing required environment variables
```
**Solution:** Set all required environment variables for your account (ACCESS_KEY, SECRET_KEY, ENDPOINT, BUCKET)

#### Connection Errors
```
Failed to connect to MinIO
```
**Solution:**
- Verify the `MINIO_{ACCOUNT}_ENDPOINT` is correct and accessible
- Check network connectivity
- Ensure MinIO server is running

### SURFdrive Issues

#### Authentication Errors (401)
```
Error: 401
```
**Solution:**
- Verify `SURFDRIVE_SHARE_TOKEN` and `SURFDRIVE_PASSWORD` are correct
- Check that the share is still active and accessible

#### File Not Found (404)
```
Error: 404
```
**Solution:**
- Verify the share URL is correct
- Check that the file exists in the shared folder

#### Network Timeout
```
Connection timeout
```
**Solution:**
- Check internet connectivity
- Verify SURFdrive service is accessible
- Try again later if service is experiencing issues

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Run linters: `make lint`
6. Commit your changes: `git commit -m "Description"`
7. Push to your fork: `git push origin feature-name`
8. Create a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Deployment

**Quick Start:** [5-Minute Trusted Publisher Setup](docs/deployment/trusted-publisher-quickstart.md) ⚡

For complete information on publishing to PyPI:
- [Trusted Publisher Quick Start](docs/deployment/trusted-publisher-quickstart.md) - Already uploaded? Start here!
- [Complete Test PyPI Setup Guide](docs/deployment/testpypi-setup.md) - First time? Read this.
- [Deployment Documentation](docs/deployment/) - Overview and troubleshooting

## Support

- Issues: https://github.com/cedanl/sdp-tools/issues
- Documentation: https://github.com/cedanl/sdp-tools/tree/main/docs
- Deployment: https://github.com/cedanl/sdp-tools/tree/main/docs/deployment

## Version

Current version: 2025.1.9

See [CHANGELOG.md](CHANGELOG.md) for version history.