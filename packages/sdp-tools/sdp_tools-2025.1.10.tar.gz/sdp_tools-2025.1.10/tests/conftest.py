"""Pytest configuration and fixtures for minio-file tests."""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "requires_minio: marks tests that require a running MinIO server")


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Auto-mark integration tests
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def package_version():
    """Get the package version."""
    import minio_file

    return minio_file.__version__


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    import shutil
    import tempfile

    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_minio_client():
    """Create a mock MinIO client for testing."""
    from unittest.mock import Mock

    client = Mock()
    client.bucket_exists.return_value = True
    client.list_buckets.return_value = []
    client.list_objects.return_value = []

    return client


@pytest.fixture(scope="session")
def check_minio_available():
    """Check if MinIO library is available."""
    try:
        import minio  # noqa: F401

        return True
    except ImportError:
        return False


# Environment fixtures
@pytest.fixture
def clean_environment():
    """Provide a clean environment without MinIO-related env vars."""
    original_env = os.environ.copy()

    # Remove MinIO-related environment variables
    minio_vars = [key for key in os.environ.keys() if key.startswith('MINIO_')]
    for var in minio_vars:
        os.environ.pop(var, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_minio_config():
    """Provide sample MinIO configuration."""
    return {
        'endpoint': 'localhost:9000',
        'access_key': 'test_access_key',
        'secret_key': 'test_secret_key',
        'secure': False,
    }


# Skip markers for conditional tests
def pytest_runtest_setup(item):
    """Setup function for each test."""
    # Skip tests that require actual MinIO server if not available
    if item.get_closest_marker("requires_minio"):
        # You could add logic here to check if MinIO server is running
        # For now, we'll skip these tests by default
        pytest.skip("MinIO server required but not available")


# Custom assertions
def assert_importable(module_name):
    """Assert that a module can be imported."""
    try:
        __import__(module_name)
    except ImportError as e:
        pytest.fail(f"Module {module_name} not importable: {e}")


def assert_callable_exists(module, function_name):
    """Assert that a callable function exists in a module."""
    assert hasattr(module, function_name), f"Function {function_name} not found in module"
    func = getattr(module, function_name)
    assert callable(func), f"{function_name} is not callable"
