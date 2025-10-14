# Production PyPI Publishing Setup

**Estimated time: 5-10 minutes**

This guide walks you through setting up automated publishing to **production PyPI** (https://pypi.org).

## Prerequisites

- ✅ Package tested and working on Test PyPI
- ✅ Ready to publish to production PyPI where millions of users can install it
- ✅ You have admin access to the GitHub repository
- ✅ You have an account on https://pypi.org

## ⚠️ Important Notes

- **Production PyPI is permanent** - You cannot delete releases, only yank them
- **Version numbers cannot be reused** - Once published, that version is locked forever
- **This makes the package publicly available** to all Python users worldwide
- **Test thoroughly on Test PyPI first** before publishing to production

## Step 1: Create Production PyPI Account (if needed)

1. Go to: https://pypi.org/account/register/
2. Create an account (different from Test PyPI)
3. Verify your email address

## Step 2: Manual Upload to Claim Package Name (First Time Only)

**⚠️ Important:** You must upload at least once manually to claim the package name before you can configure trusted publishing.

### 2.1 Create API Token

1. Go to: https://pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Token name: `sdp-tools-initial-upload`
4. Scope: **"Entire account"** (we'll create a project-scoped token later)
5. Click **"Add token"**
6. **Copy the token** - you won't see it again!

### 2.2 Build and Upload

```bash
# Make sure you're on the main branch with the latest code
git checkout main
git pull

# Build the package
uv build

# Upload to PyPI (will prompt for credentials)
uv run twine upload dist/*
# Username: __token__
# Password: <paste your token here>
```

### 2.3 Verify Upload

1. Go to: https://pypi.org/project/sdp-tools/
2. You should see your package listed!
3. Try installing it:
   ```bash
   pip install sdp-tools
   ```

## Step 3: Configure Trusted Publisher on Production PyPI

### 3.1 Navigate to Publishing Settings

Go to: https://pypi.org/manage/project/sdp-tools/settings/publishing/

### 3.2 Add GitHub as Trusted Publisher

1. Scroll to **"Publishing"** section
2. Click **"Add a new publisher"**
3. Select **"GitHub"** (should be pre-selected)

### 3.3 Fill in the Form

Enter these **EXACT** values:

| Field | Value | Notes |
|-------|-------|-------|
| **PyPI Project Name** | `sdp-tools` | Must match exactly |
| **Owner** | `cedanl` | Your GitHub username/org |
| **Repository name** | `sdp-tools` | Your repository name |
| **Workflow name** | `release.yml` | The release workflow file |
| **Environment name** | `pypi` | Must match workflow environment |

**Visual reference:**
```
┌─────────────────────────────────────┐
│ Add a new publisher                 │
├─────────────────────────────────────┤
│ Publisher: [GitHub ▼]               │
│                                     │
│ PyPI Project Name                   │
│ [sdp-tools________________]         │
│                                     │
│ Owner                               │
│ [cedanl___________________]         │
│                                     │
│ Repository name                     │
│ [sdp-tools________________]         │
│                                     │
│ Workflow name                       │
│ [release.yml______________]         │
│                                     │
│ Environment name                    │
│ [pypi_____________________]         │
│                                     │
│         [Add publisher]             │
└─────────────────────────────────────┘
```

### 3.4 Save

Click **"Add publisher"** button.

### 3.5 Verify

You should see:
```
GitHub Publishers
✓ cedanl/sdp-tools via release.yml (environment: pypi)
```

## Step 4: Create GitHub Environment

### 4.1 Navigate to Environments

Go to: https://github.com/cedanl/sdp-tools/settings/environments

### 4.2 Create Environment

1. Click **"New environment"** button
2. Name: `pypi` (exactly, lowercase)
3. Click **"Configure environment"**

### 4.3 Configure Protection Rules (Recommended)

For production, it's recommended to add protection:

- ✅ **Required reviewers**: Add yourself or team members
  - This requires manual approval before publishing to PyPI
  - Prevents accidental releases

- ✅ **Deployment branches**: Select "Protected branches only"
  - Only allows releases from `main` branch
  - Requires branch protection to be set up

### 4.4 Save

Click **"Save protection rules"**

## Step 5: Create a GitHub Release

Now that trusted publishing is configured, you can create releases.

### 5.1 Prepare for Release

Make sure all changes are committed and pushed:

```bash
git status  # Should be clean
git push origin main
```

### 5.2 Create and Push Tag

Create a tag matching the current version:

```bash
# Get current version from pyproject.toml
VERSION=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
echo "Current version: $VERSION"

# Create tag
git tag -a "v$VERSION" -m "Release version $VERSION"

# Push tag
git push origin "v$VERSION"
```

Or manually:

```bash
git tag -a v2025.1.9 -m "Release version 2025.1.9"
git push origin v2025.1.9
```

### 5.3 Watch Workflow

1. Go to: https://github.com/cedanl/sdp-tools/actions
2. Find the **"release & publish workflow"** run
3. If you configured required reviewers, **approve the deployment**:
   - Click on the workflow run
   - Click **"Review deployments"**
   - Select `pypi` checkbox
   - Click **"Approve and deploy"**

### 5.4 Monitor Progress

The workflow will:
- ✅ Build the package
- ✅ Build documentation
- ✅ Publish docs to GitHub Pages
- ✅ Publish package to PyPI

### 5.5 Create GitHub Release (Optional)

Go to: https://github.com/cedanl/sdp-tools/releases/new

- Tag: Select the tag you just created
- Release title: `v2025.1.9`
- Description: Add release notes (see CHANGELOG.md)
- Click **"Publish release"**

## Step 6: Verify Publication

### 6.1 Check PyPI

1. Go to: https://pypi.org/project/sdp-tools/
2. Verify the new version is listed
3. Check that the README displays correctly

### 6.2 Test Installation

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from PyPI
pip install sdp-tools

# Test import
python -c "from minio_file import create_connection; print('✅ Import successful!')"

# Check version
python -c "import minio_file; print(f'Version: {minio_file.__version__}')"
```

### 6.3 Verify Documentation

Go to: https://cedanl.github.io/sdp-tools/

## Troubleshooting

### Error: "invalid-publisher"

**Problem:** GitHub Actions says publisher not found.

**Solutions:**
- Double-check all values in Step 3.3 are **exactly** correct
- Verify environment name is exactly `pypi` (lowercase)
- Wait 1-2 minutes after creating publisher, then retry
- Make sure you did the initial manual upload (Step 2)

### Error: "File already exists"

**Problem:** Version already published to PyPI.

**Solution:**
- You cannot reuse version numbers on PyPI
- Bump the version in `pyproject.toml` and `__init__.py` files
- Create a new tag with the new version

### Error: "Environment protection rules not met"

**Problem:** Deployment requires approval.

**Solution:**
- Go to the workflow run page
- Click **"Review deployments"**
- Select `pypi` checkbox
- Click **"Approve and deploy"**

### Workflow Not Triggering

**Problem:** Pushing tag doesn't trigger workflow.

**Solutions:**
- Verify tag starts with `v` (e.g., `v2025.1.9`, not `2025.1.9`)
- Check workflow file has correct trigger:
  ```yaml
  on:
    push:
      tags:
        - "v*"
  ```
- Try manually triggering from Actions tab

### Documentation Not Publishing

**Problem:** Docs build fails or don't appear on GitHub Pages.

**Solutions:**
- Check if GitHub Pages is enabled in repository settings
- Verify `mkdocs.yml` configuration is correct
- Check workflow logs for build errors

## Best Practices

### 1. Version Management

- Use semantic versioning: MAJOR.MINOR.PATCH
- Our format: YYYY.M.P (calendar versioning)
- Never reuse version numbers
- Keep `pyproject.toml` and `__init__.py` files in sync

### 2. Release Checklist

Before creating a release:

- [ ] All tests passing
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] Documentation updated
- [ ] Version bumped in all files
- [ ] Tested on Test PyPI
- [ ] All changes committed and pushed

### 3. Security

- ✅ Use trusted publishing (no API tokens in GitHub)
- ✅ Use environment protection rules
- ✅ Require code review before merging to main
- ✅ Set up branch protection on main
- ⚠️ Never commit API tokens to git

### 4. Release Frequency

- Release often with small changes
- Use Test PyPI for experimental features
- Production releases should be stable and tested

## Automated Workflow Summary

Once set up, your release process is:

```bash
# 1. Make changes and commit
git add .
git commit -m "Add new feature"
git push

# 2. Bump version and create tag
git tag -a v2025.1.10 -m "Release 2025.1.10"
git push origin v2025.1.10

# 3. Workflow automatically:
#    - Builds package
#    - Publishes to PyPI
#    - Updates documentation
```

That's it! No manual uploads needed.

## Reference Values

For copy-paste convenience:

```
PyPI URL: https://pypi.org
Project URL: https://pypi.org/project/sdp-tools/
Publishing Settings: https://pypi.org/manage/project/sdp-tools/settings/publishing/

GitHub Environment: pypi
Workflow File: release.yml
Repository: cedanl/sdp-tools
```

## Next Steps

- Set up branch protection rules on `main`
- Configure automated testing before merge
- Set up changelog automation
- Consider setting up release drafter

## Support

- **PyPI Help**: https://pypi.org/help/
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Trusted Publishing**: https://docs.pypi.org/trusted-publishers/
- **Issues**: https://github.com/cedanl/sdp-tools/issues
