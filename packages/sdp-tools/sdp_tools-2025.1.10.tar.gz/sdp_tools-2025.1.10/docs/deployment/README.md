# Deployment Documentation

Documentation for deploying and publishing sdp-tools.

## Files

### `trusted-publisher-quickstart.md` ⚡

**5-minute quick start** for configuring trusted publishing after you've already uploaded to Test PyPI once.

**Start here if:**
- ✅ You've already uploaded to Test PyPI
- ✅ You just want to enable automatic publishing
- ✅ You want the fastest path to get it working

### `testpypi-setup.md` 📚

Complete guide for setting up automated publishing to Test PyPI using GitHub Actions and trusted publishing.

**Covers:**
- Creating Test PyPI account
- First-time manual upload
- Configuring trusted publisher
- Setting up GitHub environments
- Troubleshooting common issues

**Start here if:**
- ❌ You've never uploaded to Test PyPI
- ❌ You need detailed explanations
- ❌ You're new to PyPI publishing

## Quick Links

- **Test PyPI**: https://test.pypi.org/project/sdp-tools/
- **Production PyPI**: https://pypi.org/project/sdp-tools/ (when released)
- **GitHub Actions**: https://github.com/cedanl/sdp-tools/actions
- **Setup Script**: [../../scripts/setup_testpypi.sh](../../scripts/setup_testpypi.sh)

## Workflows

The project uses three main workflows:

1. **test.yml** - Run on all PRs and pushes, tests on multiple Python versions
2. **dev.yml** - Development workflow for all platforms
3. **preview.yml** - Publishes development versions to Test PyPI (requires setup)

## Publishing Process

### Test PyPI (Development)
1. Complete setup from `testpypi-setup.md`
2. Push to `main` branch
3. Workflow automatically publishes `YYYY.M.P.devN` version

### Production PyPI (Releases)
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create GitHub release/tag
4. Workflow publishes to production PyPI (when configured)