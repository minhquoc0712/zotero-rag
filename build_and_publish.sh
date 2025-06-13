#!/bin/bash
# Build and publish script for Zotero RAG package

set -e  # Exit on any error

echo "🔧 Building Zotero RAG Package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install build twine

# Lint and format code (optional)
if command -v black &> /dev/null; then
    echo "🎨 Formatting code with black..."
    black zotero_rag.py
fi

if command -v flake8 &> /dev/null; then
    echo "🔍 Linting with flake8..."
    flake8 zotero_rag.py --max-line-length=88
fi

# Run tests (if they exist)
if [ -d "tests" ]; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v
fi

# Build the package
echo "🏗️  Building package..."
python -m build

# Check the built package
echo "✅ Checking built package..."
python -m twine check dist/*

echo "📋 Package contents:"
tar -tzf dist/*.tar.gz | head -20

echo "📊 Package sizes:"
ls -lh dist/

# Verify installation works
echo "🔍 Testing installation..."
pip install dist/*.whl --force-reinstall --quiet

# Test import
python -c "import zotero_rag; print(f'✅ Package version: {zotero_rag.__version__}')"

# Test CLI
if command -v zotero-rag &> /dev/null; then
    echo "✅ CLI command available"
    zotero-rag --help > /dev/null && echo "✅ CLI help works"
else
    echo "❌ CLI command not found"
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📤 To publish to PyPI:"
echo "   Test PyPI: python -m twine upload --repository testpypi dist/*"
echo "   Real PyPI: python -m twine upload dist/*"
echo ""
echo "📥 To install from local build:"
echo "   pip install dist/zotero_rag-*.whl"
echo ""
echo "📥 Users can install with:"
echo "   pip install zotero-rag"
echo "   pip install zotero-rag[gpu]  # For GPU support"
