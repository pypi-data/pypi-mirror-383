#!/bin/bash
# Build script for the package

set -e

echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

echo "Running tests..."
pytest

echo "Checking code format..."
black --check induslabs/

echo "Building package..."
python -m build

echo "Checking distribution..."
twine check dist/*

echo ""
echo "Build complete! Distribution files:"
ls -lh dist/

echo ""
echo "To upload to Test PyPI:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI:"
echo "  twine upload dist/*"
