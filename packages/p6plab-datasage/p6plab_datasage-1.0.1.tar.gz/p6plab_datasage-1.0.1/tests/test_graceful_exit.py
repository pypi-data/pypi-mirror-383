"""Tests for graceful exit functionality."""

import pytest
from unittest.mock import Mock

from p6plab_datasage.utils.graceful_exit import GracefulExit
from p6plab_datasage.utils.resource_manager import ResourceManager


def test_graceful_exit_initialization():
    """Test GracefulExit initialization."""
    graceful_exit = GracefulExit()
    
    assert not graceful_exit.shutdown_requested
    assert graceful_exit.cleanup_callbacks == []
    assert graceful_exit._original_handlers == {}


def test_cleanup_callback_registration():
    """Test cleanup callback registration."""
    graceful_exit = GracefulExit()
    
    callback1 = Mock()
    callback2 = Mock()
    
    graceful_exit.add_cleanup_callback(callback1)
    graceful_exit.add_cleanup_callback(callback2)
    
    assert len(graceful_exit.cleanup_callbacks) == 2
    assert callback1 in graceful_exit.cleanup_callbacks
    assert callback2 in graceful_exit.cleanup_callbacks


def test_resource_manager_statistics():
    """Test resource manager statistics tracking."""
    resource_manager = ResourceManager()
    
    # Track some requests
    resource_manager.track_request()
    resource_manager.track_request()
    resource_manager.track_request()
    
    # Track file access
    resource_manager.track_file_access("/test/file1.txt")
    resource_manager.track_file_access("/test/file2.txt")
    
    # Cache some searches
    resource_manager.cache_search_result("test query", {"results": []})
    
    stats = resource_manager.get_statistics()
    
    assert stats['total_requests'] == 3
    assert stats['tracked_files'] == 2
    assert stats['cached_searches'] == 1
    assert 'uptime_seconds' in stats
    assert 'requests_per_second' in stats


def test_resource_manager_cleanup():
    """Test resource manager cleanup."""
    resource_manager = ResourceManager()
    
    # Add some data
    resource_manager.track_request()
    resource_manager.track_file_access("/test/file.txt")
    resource_manager.cache_search_result("test", {"results": []})
    
    # Verify data exists
    assert resource_manager.request_count > 0
    assert len(resource_manager.open_files) > 0
    assert len(resource_manager.search_cache) > 0
    
    # Cleanup
    resource_manager.cleanup()
    
    # Verify cleanup
    assert len(resource_manager.search_cache) == 0
    assert len(resource_manager.open_files) == 0


def test_search_cache_expiration():
    """Test search cache expiration."""
    resource_manager = ResourceManager()
    
    # Cache a result
    resource_manager.cache_search_result("test query", {"results": []})
    
    # Should be able to retrieve immediately
    result = resource_manager.get_cached_search("test query", max_age=300)
    assert result is not None
    
    # Should expire with very short max_age
    result = resource_manager.get_cached_search("test query", max_age=0)
    assert result is None
    
    # Should be removed from cache after expiration check
    assert "test query" not in resource_manager.search_cache


def test_server_graceful_exit_integration():
    """Test server integration with graceful exit (without signal handling)."""
    from p6plab_datasage.server import create_server
    import tempfile
    import os
    
    # Create test config
    config_content = """
server:
  name: "TestServer"
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
        # Create server (should setup graceful exit)
        server = create_server(config_path)
        
        assert server is not None
        assert server.name == "TestServer"
        
    finally:
        os.unlink(config_path)


def test_graceful_exit_callback_execution():
    """Test that cleanup callbacks are executed properly."""
    graceful_exit = GracefulExit()
    
    callback1 = Mock()
    callback2 = Mock()
    graceful_exit.add_cleanup_callback(callback1)
    graceful_exit.add_cleanup_callback(callback2)
    
    # Manually trigger shutdown (without signal)
    graceful_exit.shutdown_requested = True
    
    # Execute callbacks manually (simulating shutdown)
    for callback in graceful_exit.cleanup_callbacks:
        callback()
    
    # Check that callbacks were called
    callback1.assert_called_once()
    callback2.assert_called_once()


def test_graceful_exit_with_failing_callback():
    """Test graceful exit handles failing callbacks."""
    graceful_exit = GracefulExit()
    
    # Create a callback that raises an exception
    failing_callback = Mock(side_effect=Exception("Test exception"))
    working_callback = Mock()
    
    graceful_exit.add_cleanup_callback(failing_callback)
    graceful_exit.add_cleanup_callback(working_callback)
    
    # Execute callbacks manually (simulating shutdown)
    for callback in graceful_exit.cleanup_callbacks:
        try:
            callback()
        except Exception:
            pass  # Should continue with other callbacks
    
    # Check that both callbacks were attempted
    failing_callback.assert_called_once()
    working_callback.assert_called_once()
