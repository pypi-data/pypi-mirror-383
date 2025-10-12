#!/bin/bash
# Build DataSage MCP Server package using UV

set -e

echo "🔧 Building DataSage MCP Server package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package with UV
uv build

echo "✅ Package built successfully!"
echo "📦 Package contents:"
ls -la dist/
