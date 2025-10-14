# Test PyPI Trusted Publishing Setup Guide

This guide will help you set up trusted publishing for automatic uploads to Test PyPI.

## Prerequisites

- Test PyPI account (create at https://test.pypi.org/account/register/)
- Admin access to the GitHub repository

## Complete Setup Process

### Part 1: Initial Manual Upload (One-Time)

The first time you need to upload manually to register the project name on Test PyPI.

#### 1.1 Create a Test PyPI API Token

1. Go to https://test.pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Token name: `sdp-tools-upload` (or any name you prefer)
4. Scope: **"Entire account"** (for first upload)
5. Click **"Add token"**
6. **COPY THE TOKEN NOW** - you won't see it again!
7. Store it safely (e.g., in a password manager)

#### 1.2 Run the Setup Script

```bash
# From the project root
./scripts/setup_testpypi.sh
```

When prompted:
- **Username**: `__token__`
- **Password**: (paste the API token you just created)

Alternatively, do it manually:

```bash
# Build the package
uv build

# Install twine
uv pip install twine

# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

#### 1.3 Verify Upload

Go to https://test.pypi.org/project/sdp-tools/ to verify your package was uploaded.

### Part 2: Configure Trusted Publisher

Now that the project exists on Test PyPI, you can set up trusted publishing.

#### 2.1 Add Publisher on Test PyPI

1. Go to https://test.pypi.org/manage/project/sdp-tools/settings/publishing/

2. Scroll to the **"Publishing"** section

3. Click **"Add a new publisher"**

4. Select **"GitHub"** as the publisher type

5. Fill in the form with these **EXACT** values:
   ```
   PyPI Project Name: sdp-tools
   Owner: cedanl
   Repository name: sdp-tools
   Workflow name: preview.yml
   Environment name: test-pypi
   ```

6. Click **"Add"**

7. You should see a success message and the publisher in the list

### Part 3: Configure GitHub Environment

The workflow uses a GitHub environment for additional security.

#### 3.1 Create the Environment

1. Go to https://github.com/cedanl/sdp-tools

2. Click **"Settings"** tab (at the top)

3. In the left sidebar, click **"Environments"**

4. Click **"New environment"** button

5. Environment name: `test-pypi` (must be exact)

6. Click **"Configure environment"**

7. (Optional) Configure protection rules:
   - **Required reviewers**: Add yourself if you want manual approval before publishing
   - **Wait timer**: Add a delay if desired
   - **Deployment branches**: Leave as default (all branches)

8. Click **"Save protection rules"**

### Part 4: Verify Setup

#### 4.1 Test the Workflow Manually

1. Go to https://github.com/cedanl/sdp-tools/actions

2. Click on **"Stage & preview workflow"** in the left sidebar

3. Click **"Run workflow"** dropdown

4. Select branch: `main`

5. Click **"Run workflow"** button

6. Watch the workflow run - it should succeed and publish to Test PyPI

#### 4.2 Verify Published Package

1. Go to https://test.pypi.org/project/sdp-tools/

2. You should see a new development version (e.g., `2025.1.6.dev4`)

3. The version number includes `.devN` where N is the GitHub run number

### Part 5: Automatic Publishing

Once everything is configured, the workflow will automatically:

1. **Run on every push to `main`**
2. **Run tests** to ensure quality
3. **Create a development version** (e.g., `2025.1.6.dev5`)
4. **Publish to Test PyPI** automatically

## Troubleshooting

### Error: "invalid-publisher"

**Problem**: Test PyPI doesn't recognize the publisher.

**Solution**:
- Double-check all values in Step 2.1 are **exactly** correct
- Verify the environment name in Step 3.1 is `test-pypi` (no typos)
- Make sure you're looking at the correct repository on GitHub

### Error: "Project name already exists"

**Problem**: Someone else registered the name on Test PyPI.

**Solution**:
- Change the project name in `pyproject.toml`
- Update the name everywhere it's referenced
- Try the setup process again with the new name

### Error: "Environment protection rules not met"

**Problem**: GitHub environment requires approval.

**Solution**:
- Go to the Actions run page
- Click **"Review deployments"**
- Select the `test-pypi` environment
- Click **"Approve and deploy"**

### Workflow runs but doesn't publish

**Problem**: Environment not configured or workflow file incorrect.

**Solution**:
- Verify environment exists: https://github.com/cedanl/sdp-tools/settings/environments
- Check workflow file references correct environment name
- Re-run the workflow

## Testing Without Publishing

If you want to test the workflow without actually publishing:

1. Comment out the publish step in `.github/workflows/preview.yml`:
   ```yaml
   # - name: Publish distribution to Test PyPI
   #   uses: pypa/gh-action-pypi-publish@release/v1
   #   with:
   #     repository-url: https://test.pypi.org/legacy/
   ```

2. The workflow will build and test but skip publishing

## Security Notes

- **Never commit API tokens** to the repository
- Trusted publishing is more secure than API tokens
- The `test-pypi` environment adds an extra layer of protection
- You can add required reviewers to prevent accidental publishes

## For Production PyPI

When ready to publish to production PyPI (not Test PyPI):

1. Repeat the same process at https://pypi.org (not test.pypi.org)
2. Update the `release.yml` workflow (not `preview.yml`)
3. Use environment name `pypi` instead of `test-pypi`
4. Be more careful - production PyPI is permanent!

## Quick Reference

### Important URLs

- **Test PyPI**: https://test.pypi.org
- **Create Token**: https://test.pypi.org/manage/account/token/
- **Project Settings**: https://test.pypi.org/manage/project/sdp-tools/settings/publishing/
- **GitHub Environments**: https://github.com/cedanl/sdp-tools/settings/environments
- **GitHub Actions**: https://github.com/cedanl/sdp-tools/actions

### Exact Values for Trusted Publisher

```
PyPI Project Name: sdp-tools
Owner: cedanl
Repository name: sdp-tools
Workflow name: preview.yml
Environment name: test-pypi
```

Copy these values exactly when configuring on Test PyPI.