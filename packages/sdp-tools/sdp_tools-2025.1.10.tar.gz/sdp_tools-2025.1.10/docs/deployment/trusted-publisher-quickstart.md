# Trusted Publisher Quick Start Guide

**Estimated time: 5 minutes**

This guide assumes you've already uploaded your package to Test PyPI at least once. If you haven't, see [testpypi-setup.md](testpypi-setup.md) for the complete guide.

## Prerequisites

- ✅ Package already exists on Test PyPI: https://test.pypi.org/project/sdp-tools/
- ✅ You have admin access to the GitHub repository
- ✅ You're logged into Test PyPI

## Step 1: Configure Trusted Publisher on Test PyPI (3 minutes)

### 1.1 Navigate to Publishing Settings

Go to: https://test.pypi.org/manage/project/sdp-tools/settings/publishing/

(Replace `sdp-tools` with your project name if different)

### 1.2 Add Publisher

1. Scroll down to the **"Publishing"** section
2. Click the **"Add a new publisher"** button
3. Select **"GitHub"** as the publisher type (should be pre-selected)

### 1.3 Fill in the Form

Enter these **EXACT** values:

| Field | Value | Notes |
|-------|-------|-------|
| **PyPI Project Name** | `sdp-tools` | Must match your project name exactly |
| **Owner** | `cedanl` | Your GitHub username/org |
| **Repository name** | `sdp-tools` | Your repository name |
| **Workflow name** | `preview.yml` | The workflow file name |
| **Environment name** | `test-pypi` | Must match the environment in your workflow |

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
│ [preview.yml______________]         │
│                                     │
│ Environment name                    │
│ [test-pypi________________]         │
│                                     │
│         [Add publisher]             │
└─────────────────────────────────────┘
```

### 1.4 Save

Click **"Add publisher"** button at the bottom.

### 1.5 Verify

You should see a success message and the publisher listed in the "GitHub" section:

```
GitHub Publishers
✓ cedanl/sdp-tools via preview.yml (environment: test-pypi)
```

## Step 2: Create GitHub Environment (2 minutes)

### 2.1 Navigate to Environments

Go to: https://github.com/cedanl/sdp-tools/settings/environments

Or navigate manually:
1. Go to your repository: https://github.com/cedanl/sdp-tools
2. Click **"Settings"** tab (top of page)
3. Click **"Environments"** in left sidebar (under "Code and automation")

### 2.2 Create Environment

1. Click **"New environment"** button (green button, top right)
2. Enter environment name: `test-pypi`
   - ⚠️ **Must be exactly** `test-pypi` (lowercase, with hyphen)
   - This must match what you entered in Step 1.3
3. Click **"Configure environment"** button

### 2.3 Configure Protection Rules (Optional)

You can add protection rules if you want:

- ✅ **Required reviewers**: Add yourself if you want to approve each deployment manually
- ✅ **Wait timer**: Add a delay (in minutes) before deployment
- ✅ **Deployment branches**: Limit which branches can deploy (leave as "All branches" for now)

For automatic publishing without approval, **leave all options unchecked**.

### 2.4 Save

Click **"Save protection rules"** button at the bottom.

## Step 3: Test the Setup (30 seconds)

### 3.1 Trigger Workflow Manually

1. Go to: https://github.com/cedanl/sdp-tools/actions
2. Click **"Stage & preview workflow"** in the left sidebar
3. Click **"Run workflow"** button (right side)
4. Dropdown appears - select branch: `main`
5. Click green **"Run workflow"** button

### 3.2 Watch the Workflow

1. The workflow will appear in the list (may take a few seconds)
2. Click on the workflow run to see details
3. Watch the steps execute:
   - ✅ Install dependencies
   - ✅ Run tests
   - ✅ Create development version
   - ✅ Build package
   - ✅ Publish to Test PyPI

### 3.3 Verify Publication

1. Go to: https://test.pypi.org/project/sdp-tools/#history
2. You should see a new version like: `2025.1.6.dev4` (number will vary)
3. The version number includes `.devN` where `N` is the GitHub Actions run number

## ✅ Success!

Your setup is complete! From now on, every push to the `main` branch will:

1. **Run all tests** to ensure quality
2. **Create a development version** (e.g., `2025.1.6.dev5`)
3. **Automatically publish** to Test PyPI

## Troubleshooting

### Error: "invalid-publisher" Still Appears

**Problem:** Workflow still says publisher not found.

**Solutions:**
- Double-check all values in Step 1.3 are **exactly** correct (no typos!)
- Verify the environment name in Step 2.2 is exactly `test-pypi`
- Wait 1-2 minutes after creating the publisher, then try again
- Make sure you created the publisher for the **correct project** on Test PyPI

### Error: "Environment protection rules not met"

**Problem:** GitHub requires approval before deploying.

**Solutions:**
- Go to the workflow run page
- Click **"Review deployments"** button
- Select `test-pypi` checkbox
- Click **"Approve and deploy"**

Or remove protection rules:
1. Go to: https://github.com/cedanl/sdp-tools/settings/environments
2. Click on `test-pypi` environment
3. Remove all protection rules
4. Save

### Workflow Runs But Doesn't Publish

**Problem:** Workflow completes but no new version on Test PyPI.

**Solutions:**
- Check workflow logs for errors
- Verify the publish step ran (look for "Uploading distributions")
- Ensure tests passed (publish step is skipped if tests fail)

### Wrong Version Number Published

**Problem:** Published version doesn't include `.devN` suffix.

**Solution:**
- This is normal for the `release.yml` workflow (production releases)
- The `preview.yml` workflow should add `.devN`
- Check which workflow ran: https://github.com/cedanl/sdp-tools/actions

## Next Steps

### For Production PyPI

When ready to publish to production PyPI (https://pypi.org):

1. Repeat this process at https://pypi.org (not test.pypi.org)
2. Use the `release.yml` workflow (not `preview.yml`)
3. Use environment name `pypi` (not `test-pypi`)
4. Create a GitHub release/tag to trigger publishing

### Disable Test PyPI Auto-Publishing

If you want to stop auto-publishing to Test PyPI:

1. Edit `.github/workflows/preview.yml`
2. Change `on: push:` to `on: workflow_dispatch:`
3. This makes it manual-trigger only

### Monitor Publications

- **Test PyPI Project**: https://test.pypi.org/project/sdp-tools/
- **GitHub Actions**: https://github.com/cedanl/sdp-tools/actions
- **Workflow Runs**: https://github.com/cedanl/sdp-tools/actions/workflows/preview.yml

## Reference Values

Keep these handy for copy-paste:

```
PyPI Project Name: sdp-tools
Owner: cedanl
Repository name: sdp-tools
Workflow name: preview.yml
Environment name: test-pypi
```

## Support

- **Test PyPI Docs**: https://test.pypi.org/help/
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Trusted Publishing Guide**: https://docs.pypi.org/trusted-publishers/
- **Troubleshooting**: https://docs.pypi.org/trusted-publishers/troubleshooting/

## Complete Setup Guide

For more detailed information and initial setup, see:
- [Full Test PyPI Setup Guide](testpypi-setup.md)
- [Deployment Documentation](README.md)