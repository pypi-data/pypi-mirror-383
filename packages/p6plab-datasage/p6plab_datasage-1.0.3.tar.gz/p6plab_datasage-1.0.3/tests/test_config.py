"""Tests for configuration module."""

import os
import tempfile
import pytest
from pathlib import Path

from p6plab_datasage.config import load_config, get_allowed_paths, DEFAULT_CONFIG


def test_default_config():
    """Test default configuration values."""
    config = load_config("nonexistent.yaml")
    
    assert config["server"]["name"] == "DataSage"
    assert config["server"]["description"] == "Local file server for AI assistants"
    assert config["settings"]["max_depth"] == 10
    assert config["settings"]["max_file_size"] == 10485760
    assert ".exe" in config["settings"]["excluded_extensions"]


def test_yaml_config_loading():
    """Test loading configuration from YAML file."""
    config_content = """
server:
  name: "TestSage"
  description: "Test server"
paths:
  - path: "/tmp"
settings:
  max_depth: 5
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        config = load_config(config_path)
        
        assert config["server"]["name"] == "TestSage"
        assert config["server"]["description"] == "Test server"
        assert config["settings"]["max_depth"] == 5
        assert len(config["paths"]) == 1
        assert config["paths"][0]["path"] == "/tmp"
    finally:
        os.unlink(config_path)


def test_environment_variable_overrides():
    """Test environment variable overrides."""
    # Store original values
    original_values = {}
    env_vars = ["DATASAGE_NAME", "DATASAGE_DESCRIPTION", "DATASAGE_PATHS", "DATASAGE_MAX_DEPTH"]
    
    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
    
    # Set environment variables
    os.environ["DATASAGE_NAME"] = "EnvSage"
    os.environ["DATASAGE_DESCRIPTION"] = "Environment server"
    os.environ["DATASAGE_PATHS"] = "/tmp,/var"
    os.environ["DATASAGE_MAX_DEPTH"] = "3"
    
    try:
        config = load_config("nonexistent.yaml")
        
        assert config["server"]["name"] == "EnvSage"
        assert config["server"]["description"] == "Environment server"
        assert config["settings"]["max_depth"] == 3
        assert len(config["paths"]) == 2
        assert config["paths"][0]["path"] == "/tmp"
        assert config["paths"][1]["path"] == "/var"
    finally:
        # Clean up environment variables
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
            # Restore original values
            if var in original_values:
                os.environ[var] = original_values[var]


def test_get_allowed_paths():
    """Test getting allowed paths from configuration."""
    config = {
        "paths": [
            {"path": "/tmp"},
            "/var/log",
            {"path": "~/Documents"}
        ]
    }
    
    paths = get_allowed_paths(config)
    
    assert len(paths) == 3
    assert all(isinstance(p, Path) for p in paths)
    # Use resolved paths since /tmp might resolve to /private/tmp on macOS
    assert paths[0].name == "tmp"
    assert paths[1].name == "log"
    # Third path should be expanded home directory


def test_config_validation():
    """Test configuration validation."""
    from p6plab_datasage.config import _validate_config
    
    # Test invalid max_depth
    with pytest.raises(ValueError, match="max_depth must be an integer"):
        config = {
            "server": {"name": "test"},
            "paths": [],
            "settings": {"max_depth": 0, "max_file_size": 1000}
        }
        _validate_config(config)
    
    # Test invalid max_file_size
    with pytest.raises(ValueError, match="max_file_size must be a positive integer"):
        config = {
            "server": {"name": "test"},
            "paths": [],
            "settings": {"max_depth": 5, "max_file_size": -1}
        }
        _validate_config(config)
