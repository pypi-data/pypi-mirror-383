# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**sdp-tools** (formerly minio-uploader) is a Python tool for managing MinIO connections and file transfers. The core functionality is provided through the `minio_file` class which handles multi-account MinIO operations using environment-based configuration.

## Development Commands

### Setup
```bash
# Install in development mode with all dependencies
make install-dev
# or
uv pip install -e ".[dev,test]"

# Install pre-commit hooks
make install-pre-commit
```

### Testing
```bash
# Run all tests
make test

# Run fast tests only (skip slow tests marked with @pytest.mark.slow)
make test-fast

# Run specific test suites
make test-imports          # Test package imports
make test-functionality    # Test core functionality
make test-build           # Test package building

# Run tests with coverage
make test-coverage

# Quick development test (imports + fast tests)
make quick-test
```

### Code Quality
```bash
# Format code (black + isort)
make format

# Run all linters (black, isort, flake8)
make lint

# Run all quality checks (lint + fast tests)
make check

# Run pre-commit checks manually
make pre-commit
```

### Building
```bash
# Build package distributions
make build

# Build and verify with twine
make build-check

# Simulate full CI pipeline
make ci

# Check release readiness
make release-check
```

### Documentation
```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve
```

## Architecture

### Multi-Account Configuration System

The package supports multiple MinIO accounts (WO, HO, ML, VIZ) through environment variable naming patterns. Each account uses a prefix pattern:

```
MINIO_{ACCOUNT}_BUCKET
MINIO_{ACCOUNT}_ACCESS_KEY
MINIO_{ACCOUNT}_SECRET_KEY
MINIO_{ACCOUNT}_ENDPOINT
```

**Critical**: The `minio_file` class validates account names in `__init__` and will raise an error for invalid accounts. This validation is central to the security model.

### Core Class: `minio_file`

Located in `src/minio_file/minio_file.py`. Key methods:
- `__init__(account)`: Initializes client for specified account (WO/HO/ML/VIZ)
- `_get_credentials()`: Retrieves environment variables for the account
- `_get_client()`: Creates MinIO client with proper endpoint and security settings
- `upload_file(file_name, full_name)`: Upload files to MinIO
- `download_file(file_name, full_name)`: Download files from MinIO
- `get_file_list()`: List all objects in the bucket
- `get_buckets()`: Retrieve all available buckets

The CLI entry point is defined as `sdp-tools` in pyproject.toml and maps to `sdp_tools.sdp_tools:main`.

### Package Structure

```
src/
  minio_file/         # Note: directory is minio_file, not sdp_tools
    __init__.py       # Version and exports
    minio_file.py     # Main implementation
```

**Important**: Despite the package name being `sdp-tools`, the actual module directory is `minio_file` and imports use `sdp_tools`. The pyproject.toml maps this correctly with `[tool.hatch.build.targets.wheel]`.

## Code Style

### Formatting Rules (enforced by pre-commit)
- **Black**: Line length 120 (pyproject.toml) vs 128 (pre-commit) - be aware of this discrepancy
- **isort**: Multi-line mode 3, trailing comma, line length 120
- **flake8**: Max line length 128, ignores B008,D202,F541,W503
- **docstring-convention**: Google style

### Pre-commit Hooks
The repository uses pre-commit with:
- Standard hooks (trailing whitespace, end-of-file-fixer, yaml/json/toml checks)
- isort with black profile
- black formatting
- flake8 with docstrings (flake8-docstrings, flake8-bugbear, flake8-comprehensions)
- bandit security checks (excludes tests/)
- pycln for unused imports

## Testing Strategy

Tests are organized in `tests/`:
- `test_imports.py`: Package import validation
- `test_functionality.py`: Core functionality tests
- `test_and_build_distribution.py`: Build and distribution tests

**Test markers** (defined in pyproject.toml):
- `slow`: Long-running tests (excluded in CI with `-m "not slow"`)
- `integration`: Integration tests
- `requires_minio`: Tests requiring running MinIO server

## CI/CD Pipeline

GitHub Actions workflows in `.github/workflows/`:

### test.yml (Main CI)
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Runs: flake8, black check, isort check, mypy (non-blocking), pytest with coverage
- Build job: Creates distributions, validates with twine, tests wheel installation
- Uses `uv` for all dependency management and test execution

### Other Workflows
- `dev.yml`: Development builds
- `preview.yml`: Preview deployments
- `release.yml`: Release automation

## Version Management

Uses `bump-my-version` for version management:
- Current version: 2025.1.6
- Version locations: `src/sdp_tools/__init__.py`, `pyproject.toml`
- Format: YYYY.MINOR.PATCH with optional .postN.devN suffix
- Commits created with `--no-verify` flag

## Common Gotchas

1. **Module naming inconsistency**: Package is `sdp-tools`, directory is `minio_file`, imports are `sdp_tools` or `minio_file`
2. **Line length discrepancy**: Black config (120) differs from pre-commit (128) and flake8 (128)
3. **Account validation**: Only WO, HO, ML, VIZ are valid account names
4. **Test exclusions**: Use `-m "not slow"` to skip slow tests in development
5. **uv dependency**: The project uses `uv` instead of pip/poetry for dependency management