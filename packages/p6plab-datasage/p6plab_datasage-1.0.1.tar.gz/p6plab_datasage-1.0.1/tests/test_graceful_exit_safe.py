"""Pytest-safe tests for graceful exit functionality."""

import pytest
import sys
from unittest.mock import Mock, patch


def test_resource_manager_basic():
    """Test ResourceManager basic functionality."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    
    rm = ResourceManager()
    
    # Test request tracking
    rm.track_request()
    rm.track_request()
    assert rm.request_count == 2
    
    # Test file tracking
    rm.track_file_access('/test/file.txt')
    assert len(rm.open_files) == 1
    rm.untrack_file_access('/test/file.txt')
    assert len(rm.open_files) == 0
    
    # Test search caching
    rm.cache_search_result('test', {'results': []})
    result = rm.get_cached_search('test')
    assert result is not None
    
    # Test cleanup
    rm.cleanup()
    assert len(rm.search_cache) == 0


def test_resource_manager_statistics():
    """Test ResourceManager statistics."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    
    rm = ResourceManager()
    rm.track_request()
    rm.track_request()
    rm.track_file_access('/test/file.txt')
    rm.cache_search_result('query', {'results': []})
    
    stats = rm.get_statistics()
    assert stats['total_requests'] == 2
    assert stats['tracked_files'] == 1
    assert stats['cached_searches'] == 1
    assert 'uptime_seconds' in stats


def test_graceful_exit_callbacks():
    """Test GracefulExit callback system."""
    from p6plab_datasage.utils.graceful_exit import GracefulExit
    
    ge = GracefulExit()
    
    callback1 = Mock()
    callback2 = Mock()
    
    ge.add_cleanup_callback(callback1)
    ge.add_cleanup_callback(callback2)
    
    assert len(ge.cleanup_callbacks) == 2
    
    # Manually execute callbacks (without signals)
    for callback in ge.cleanup_callbacks:
        callback()
    
    callback1.assert_called_once()
    callback2.assert_called_once()


@patch('signal.signal')
def test_graceful_exit_signal_setup(mock_signal):
    """Test signal handler setup (mocked)."""
    from p6plab_datasage.utils.graceful_exit import GracefulExit
    import signal
    
    ge = GracefulExit()
    ge.setup_signal_handlers()
    
    # Verify signal.signal was called for SIGINT and SIGTERM
    assert mock_signal.call_count == 2
    
    # Check that SIGINT and SIGTERM were registered
    call_signals = [call.args[0] for call in mock_signal.call_args_list]
    assert signal.SIGINT in call_signals
    assert signal.SIGTERM in call_signals


def test_cache_expiration():
    """Test search cache expiration."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    
    rm = ResourceManager()
    
    # Cache a result
    rm.cache_search_result("test query", {"results": []})
    
    # Should retrieve immediately
    result = rm.get_cached_search("test query", max_age=300)
    assert result is not None
    
    # Should expire with zero max_age
    result = rm.get_cached_search("test query", max_age=0)
    assert result is None
