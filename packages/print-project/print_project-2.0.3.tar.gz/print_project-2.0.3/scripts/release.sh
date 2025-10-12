#!/bin/bash
# release.sh - Automated PyPI release script for print-project

set -e

VERSION=${1:-$(cat VERSION)}

echo "🚀 Releasing print-project v$VERSION to PyPI"
echo "=============================================="

# Verify we're in the right directory
if [ ! -f "print_project.py" ]; then
    echo "❌ Error: Must run from print-project directory"
    exit 1
fi

# Check if required tools are installed
command -v python >/dev/null 2>&1 || { echo "❌ Python is required but not installed."; exit 1; }
command -v twine >/dev/null 2>&1 || { echo "❌ twine is required. Install with: pip install twine"; exit 1; }

# Update version in pyproject.toml
echo "📝 Updating version to $VERSION..."
if command -v sed >/dev/null 2>&1; then
    sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
else
    echo "⚠️  Please manually update version in pyproject.toml to $VERSION"
fi

# Update VERSION file
echo "$VERSION" > VERSION

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build package
echo "📦 Building package..."
python -m build

echo "📋 Package contents:"
ls -la dist/

# Verify package
echo "🔍 Verifying package..."
python -m twine check dist/*

# Upload to Test PyPI first
echo ""
echo "🧪 Upload to Test PyPI first? (Y/n)"
read -r response
if [[ ! "$response" =~ ^[Nn]$ ]]; then
    echo "🧪 Uploading to Test PyPI..."
    python -m twine upload --repository testpypi dist/*
    
    echo "✅ Uploaded to Test PyPI"
    echo "🔗 View at: https://test.pypi.org/project/print-project/$VERSION/"
    echo ""
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ print-project==$VERSION"
    echo ""
fi

# Confirm production upload
echo "🌟 Upload to production PyPI? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🌟 Uploading to production PyPI..."
    python -m twine upload dist/*
    
    echo ""
    echo "🎉 Successfully released print-project v$VERSION!"
    echo "🔗 View at: https://pypi.org/project/print-project/$VERSION/"
    echo ""
    echo "📦 Users can now install with:"
    echo "  pip install print-project"
    echo ""
    echo "🏷️  Don't forget to:"
    echo "  1. git tag v$VERSION"
    echo "  2. git push --tags"
    echo "  3. Create GitHub release"
    echo "  4. Update documentation"
else
    echo "⏸️  Skipped production upload"
    echo "📋 To upload later: python -m twine upload dist/*"
fi

echo ""
echo "✅ Release process completed!"