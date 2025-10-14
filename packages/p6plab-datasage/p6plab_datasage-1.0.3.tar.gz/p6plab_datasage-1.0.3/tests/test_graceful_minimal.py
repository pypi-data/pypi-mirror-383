"""Minimal isolated tests for graceful exit components."""

def test_resource_manager_import():
    """Test ResourceManager can be imported and used."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    rm = ResourceManager()
    assert rm.request_count == 0
    assert len(rm.open_files) == 0
    assert len(rm.search_cache) == 0


def test_resource_manager_requests():
    """Test request tracking."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    rm = ResourceManager()
    
    rm.track_request()
    rm.track_request()
    
    assert rm.request_count == 2


def test_resource_manager_files():
    """Test file tracking."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    rm = ResourceManager()
    
    rm.track_file_access('/test/file.txt')
    assert len(rm.open_files) == 1
    
    rm.untrack_file_access('/test/file.txt')
    assert len(rm.open_files) == 0


def test_resource_manager_cache():
    """Test search caching."""
    from p6plab_datasage.utils.resource_manager import ResourceManager
    rm = ResourceManager()
    
    rm.cache_search_result('test', {'results': []})
    result = rm.get_cached_search('test')
    assert result is not None


def test_graceful_exit_import():
    """Test GracefulExit can be imported."""
    from p6plab_datasage.utils.graceful_exit import GracefulExit
    ge = GracefulExit()
    assert not ge.shutdown_requested
    assert len(ge.cleanup_callbacks) == 0
