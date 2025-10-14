#!/bin/bash
# Publish DataSage MCP Server to PyPI using UV

set -e

# Default to test PyPI
TARGET="test"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            TARGET="test"
            shift
            ;;
        --main)
            TARGET="main"
            shift
            ;;
        *)
            echo "Usage: $0 [--test|--main]"
            echo "  --test: Publish to Test PyPI (default)"
            echo "  --main: Publish to main PyPI"
            exit 1
            ;;
    esac
done

if [ ! -d "dist" ]; then
    echo "❌ No dist/ directory found. Run build.sh first."
    exit 1
fi

if [ "$TARGET" = "test" ]; then
    echo "🧪 Publishing DataSage MCP Server to Test PyPI..."
    # Read credentials from ~/.pypirc
    TESTPYPI_PASSWORD=$(grep -A2 '\[testpypi\]' ~/.pypirc | grep password | cut -d'=' -f2 | xargs)
    uv publish --publish-url https://test.pypi.org/legacy/ --username __token__ --password "$TESTPYPI_PASSWORD"
    echo "✅ Package published to Test PyPI successfully!"
    echo "📦 Package available at: https://test.pypi.org/project/p6plab-datasage/"
    echo "🔍 Test installation: uvx --index https://test.pypi.org/simple/ p6plab-datasage"
else
    echo "🚀 Publishing DataSage MCP Server to PyPI..."
    # Read credentials from ~/.pypirc
    PYPI_PASSWORD=$(grep -A2 '\[pypi\]' ~/.pypirc | grep password | cut -d'=' -f2 | xargs)
    uv publish --username __token__ --password "$PYPI_PASSWORD"
    echo "✅ Package published successfully!"
    echo "📦 Package available at: https://pypi.org/project/p6plab-datasage/"
fi
