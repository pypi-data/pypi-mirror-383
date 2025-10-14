#!/bin/bash
# Helper script to set up Test PyPI for the first time

set -e

echo "🚀 Setting up Test PyPI Publishing"
echo "=================================="
echo ""

# Check if version already exists
echo "Step 0: Checking for existing uploads..."
CURRENT_VERSION=$(python -c "import toml; print(toml.load(open('pyproject.toml'))['project']['version'])")
echo "Current version: $CURRENT_VERSION"
echo ""
echo "⚠️  NOTE: If this version already exists on Test PyPI, this will fail."
echo "   The automated workflow uses .devN versions to avoid conflicts."
echo ""
read -p "Continue anyway? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Use the GitHub Actions workflow for automatic publishing."
    exit 1
fi

echo ""
echo "Step 1: Building package..."
uv build

echo ""
echo "Step 2: Uploading to Test PyPI..."
echo ""
echo "📝 IMPORTANT: You'll need to authenticate with Test PyPI"
echo "   - Create an API token at: https://test.pypi.org/manage/account/token/"
echo "   - Use '__token__' as the username"
echo "   - Use your API token as the password"
echo ""

read -p "Press Enter when you're ready to upload..."

# Upload to Test PyPI
uv run twine upload --repository testpypi dist/*

echo ""
echo "✅ Upload complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to: https://test.pypi.org/manage/project/sdp-tools/settings/publishing/"
echo "2. Click 'Add a new publisher'"
echo "3. Fill in these EXACT values:"
echo "   - PyPI Project Name: sdp-tools"
echo "   - Owner: cedanl"
echo "   - Repository name: sdp-tools"
echo "   - Workflow name: preview.yml"
echo "   - Environment name: test-pypi"
echo "4. Go to GitHub: https://github.com/cedanl/sdp-tools/settings/environments"
echo "5. Create an environment named: test-pypi"
echo ""
echo "After completing these steps, automatic publishing will work!"