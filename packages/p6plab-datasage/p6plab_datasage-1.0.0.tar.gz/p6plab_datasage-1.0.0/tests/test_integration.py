"""Integration tests for DataSage MCP server."""

import tempfile
import json
import os
import pytest
from pathlib import Path

from p6plab_datasage.server import create_server


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up DATASAGE environment variables before and after each test."""
    # Store original values
    original_values = {}
    datasage_vars = [k for k in os.environ.keys() if k.startswith('DATASAGE')]
    
    for var in datasage_vars:
        original_values[var] = os.environ[var]
        del os.environ[var]
    
    yield
    
    # Clean up any new variables and restore originals
    current_datasage_vars = [k for k in os.environ.keys() if k.startswith('DATASAGE')]
    for var in current_datasage_vars:
        del os.environ[var]
    
    for var, value in original_values.items():
        os.environ[var] = value


def test_server_creation():
    """Test basic server creation."""
    # Create temporary config
    config_content = """
server:
  name: "TestDataSage"
  description: "Test server"
paths:
  - path: "/tmp"
settings:
  max_depth: 2
  max_file_size: 1048576
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        server = create_server(config_path)
        
        # Check server properties
        assert server.name == "TestDataSage"
        
        # Check that server was created successfully
        assert server is not None
        
    finally:
        Path(config_path).unlink()


def test_server_with_test_files():
    """Test server functionality with actual test files."""
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "test.txt").write_text("Hello world\nThis is a test file.")
        (temp_path / "test.py").write_text("print('Hello Python')")
        (temp_path / "subdir").mkdir()
        (temp_path / "subdir" / "nested.md").write_text("# Nested File\nContent here.")
        
        # Create config pointing to temp directory
        config_content = f"""
server:
  name: "TestDataSage"
paths:
  - path: "{temp_dir}"
settings:
  max_depth: 3
  max_file_size: 1048576
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            server = create_server(config_path)
            
            # Test would require FastMCP client to actually call tools
            # For now, just verify server creation succeeds
            assert server.name == "TestDataSage"
            
        finally:
            Path(config_path).unlink()


def test_server_error_handling():
    """Test server error handling with invalid configuration."""
    # Test with non-existent config file
    server = create_server("nonexistent.yaml")
    assert server.name == "DataSage"  # Should use defaults
    
    # Test with invalid YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_path = f.name
    
    try:
        server = create_server(config_path)
        # Should still create server with defaults despite invalid YAML
        assert server.name == "DataSage"
        
    finally:
        Path(config_path).unlink()
