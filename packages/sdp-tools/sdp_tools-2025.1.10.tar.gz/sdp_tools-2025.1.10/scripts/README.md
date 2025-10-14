# Scripts

Helper scripts for development and deployment.

## Available Scripts

### `setup_testpypi.sh`

One-time setup script for configuring Test PyPI publishing.

**Usage:**
```bash
./scripts/setup_testpypi.sh
```

**What it does:**
1. Builds the package
2. Uploads to Test PyPI (requires API token)
3. Shows next steps for configuring trusted publishing

**Prerequisites:**
- Test PyPI account
- API token from https://test.pypi.org/manage/account/token/

**See also:** [docs/deployment/testpypi-setup.md](../docs/deployment/testpypi-setup.md) for complete setup guide.