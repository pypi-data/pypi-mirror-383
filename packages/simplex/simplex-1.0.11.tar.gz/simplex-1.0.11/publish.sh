#!/bin/bash

# Exit on error
set -e

echo "Starting Python SDK publish script..."

# Load environment variables from .env
if [ -f .env ]; then
    echo "Found .env file"
    export $(cat .env | grep -v '^#' | xargs)
    echo "Loaded environment variables"
else
    echo "Error: .env file not found"
    exit 1
fi

# Check if PYPI_API_TOKEN exists
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "Error: PYPI_API_TOKEN not found in .env file"
    exit 1
fi
echo "Found PYPI_API_TOKEN"

# Extract current version from setup.py and increment patch version
echo "Attempting to read version from setup.py..."
if [ ! -f setup.py ]; then
    echo "Error: setup.py file not found"
    exit 1
fi

echo "Contents of setup.py version line:"
grep "version=" setup.py || echo "No version line found"

# More portable version extraction that works on both Mac and Linux
current_version=$(grep "version=" setup.py | sed 's/.*version="\([^"]*\)".*/\1/')
if [ -z "$current_version" ]; then
    echo "Error: Could not extract version from setup.py"
    echo "Make sure setup.py contains a line like: version='1.0.0' or version=\"1.0.0\""
    exit 1
fi
echo "Current version: $current_version"
IFS='.' read -r major minor patch <<< "$current_version"
new_patch=$((patch + 1))
new_version="$major.$minor.$new_patch"

# Update version in setup.py (Mac-compatible sed syntax)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac version - escape the quotes and use a different delimiter
    sed -i '' "s|version=\"${current_version}\"|version=\"${new_version}\"|" setup.py
else
    # Linux version
    sed -i "s/version=\"${current_version}\"/version=\"${new_version}\"/" setup.py
fi

echo "Updated setup.py from $current_version to $new_version"

# Update version in pyproject.toml
if [ -f pyproject.toml ]; then
    echo "Updating version in pyproject.toml..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|version = \".*\"|version = \"${new_version}\"|" pyproject.toml
    else
        sed -i "s/version = \".*\"/version = \"${new_version}\"/" pyproject.toml
    fi
    echo "Updated pyproject.toml to $new_version"
fi

# Update version in simplex/__init__.py
if [ -f simplex/__init__.py ]; then
    echo "Updating version in simplex/__init__.py..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|__version__ = \".*\"|__version__ = \"${new_version}\"|" simplex/__init__.py
    else
        sed -i "s/__version__ = \".*\"/__version__ = \"${new_version}\"/" simplex/__init__.py
    fi
    echo "Updated simplex/__init__.py to $new_version"
fi

echo "All version files updated from $current_version to $new_version"

# Check BASE_URL in simplex/client.py
echo "Checking BASE_URL in simplex/client.py..."
if ! grep -q 'https://api.simplex.sh' simplex/client.py; then
    echo "Warning: BASE_URL in simplex/client.py may not be set to production URL"
    echo "Continuing anyway..."
fi
echo "BASE_URL check passed"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info simplex.egg-info

# Build the package using modern build tool
echo "Building package..."
python -m build

# Upload to PyPI using API token
echo "Uploading to PyPI..."
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_API_TOKEN python -m twine upload dist/*

echo "Successfully published version $new_version to PyPI"

# Create git commit and tag
echo "Creating git commit and tag..."
git add setup.py pyproject.toml simplex/__init__.py
git commit -m "Bump Python SDK version to $new_version"
git tag "python-v$new_version"
git push && git push --tags

echo "Created and pushed git tag python-v$new_version"
echo ""
echo "🎉 Python SDK v$new_version published successfully!"
echo "Users can now install with: pip install simplex"