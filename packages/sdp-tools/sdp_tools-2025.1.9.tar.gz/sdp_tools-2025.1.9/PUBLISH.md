# Quick Publish Guide

Fast reference for publishing releases.

## First Time Setup

See [docs/deployment/pypi-production-setup.md](docs/deployment/pypi-production-setup.md) for complete setup instructions.

## Regular Release Process

### 1. Prepare Release

```bash
# Make sure everything is committed
git status

# Run tests
make test

# Update CHANGELOG.md with changes
# Update version in README.md if needed
```

### 2. Bump Version

Update version in these files:
- `pyproject.toml` - line 7: `version = "YYYY.M.P"`
- `src/minio_file/__init__.py` - line 3: `__version__ = "YYYY.M.P"`
- `src/surfdrive/__init__.py` - line 3: `__version__ = "YYYY.M.P"`
- `README.md` - near bottom: `Current version: YYYY.M.P`

Or use the bump script:
```bash
# Bump patch version
make bump-patch

# Or manually
./scripts/bump_version.sh 2025.1.10
```

### 3. Commit and Push

```bash
git add .
git commit -m "Bump version to YYYY.M.P"
git push origin main
```

### 4. Create and Push Tag

```bash
# Get current version
VERSION=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)

# Create tag
git tag -a "v$VERSION" -m "Release version $VERSION"

# Push tag (this triggers the workflow)
git push origin "v$VERSION"
```

### 5. Monitor Workflow

1. Go to: https://github.com/cedanl/sdp-tools/actions
2. Watch the "release & publish workflow" run
3. If using environment protection, approve deployment
4. Wait for completion (~2-3 minutes)

### 6. Verify

```bash
# Check PyPI
open https://pypi.org/project/sdp-tools/

# Test installation
python -m venv test-env
source test-env/bin/activate
pip install sdp-tools
python -c "from minio_file import create_connection; print('✅ Works!')"
```

## Emergency: Yank a Release

If you published a broken release:

```bash
# Install twine if needed
pip install twine

# Yank the release (doesn't delete, but warns users)
twine yank sdp-tools <VERSION> -r pypi
```

Note: You cannot delete releases from PyPI, only yank them.

## Common Issues

**Tag doesn't trigger workflow**
- Make sure tag starts with `v` (e.g., `v2025.1.9`)
- Check you pushed the tag: `git push origin v2025.1.9`

**Version already exists**
- Bump to a new version number
- You cannot reuse version numbers on PyPI

**Tests failing in CI**
- Fix tests before releasing
- Check GitHub Actions logs for details

**Need to test first?**
- Use Test PyPI: Push to `main` (auto-publishes dev version)
- Install with: `pip install -i https://test.pypi.org/simple/ sdp-tools`

## Version Numbering

We use calendar versioning: `YYYY.M.P`

- `YYYY` - Year (e.g., 2025)
- `M` - Month number (1-12, no leading zero)
- `P` - Patch number (0, 1, 2, ...)

Examples:
- `2025.1.9` - 9th release in January 2025
- `2025.2.0` - First release in February 2025
- `2025.12.15` - 15th release in December 2025

## Pre-Release Checklist

- [ ] All tests passing (`make test`)
- [ ] Code formatted (`make format`)
- [ ] Linters passing (`make lint`)
- [ ] CHANGELOG.md updated
- [ ] Version bumped in all files
- [ ] Documentation updated
- [ ] Tested on Test PyPI (optional but recommended)
- [ ] README examples work
- [ ] Breaking changes documented

## Links

- **Production PyPI**: https://pypi.org/project/sdp-tools/
- **Test PyPI**: https://test.pypi.org/project/sdp-tools/
- **GitHub Releases**: https://github.com/cedanl/sdp-tools/releases
- **GitHub Actions**: https://github.com/cedanl/sdp-tools/actions
- **Documentation**: https://cedanl.github.io/sdp-tools/

## Help

For detailed instructions, see:
- [Production PyPI Setup](docs/deployment/pypi-production-setup.md)
- [Test PyPI Setup](docs/deployment/testpypi-setup.md)
- [Trusted Publisher Quick Start](docs/deployment/trusted-publisher-quickstart.md)
