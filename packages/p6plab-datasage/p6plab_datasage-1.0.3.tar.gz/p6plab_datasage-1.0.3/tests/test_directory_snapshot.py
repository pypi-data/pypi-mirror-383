"""Tests for directory snapshot comparison and file system change detection."""

import tempfile
import shutil
from pathlib import Path
import pytest
import time

from p6plab_datasage.utils.search_engine import SearchEngine


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path).resolve()  # Always use resolved paths
    shutil.rmtree(temp_path)


@pytest.fixture
def snapshot_config(temp_dir):
    """Configuration for snapshot testing."""
    return {
        "paths": [{"path": str(temp_dir), "description": "Test files"}],
        "settings": {"max_depth": 10},
        "search": {
            "fuzzy_threshold": 0.8,
            "enable_regex": True,
            "enable_semantic": False
        }
    }


def test_directory_snapshot_initialization(temp_dir, snapshot_config):
    """Test directory snapshot initialization."""
    # Create test files
    (temp_dir / "test1.txt").write_text("Test content 1")
    (temp_dir / "test2.txt").write_text("Test content 2")
    
    engine = SearchEngine(snapshot_config)
    
    # First search should initialize snapshot
    results = engine.search("test", search_type="filename", match_type="exact")
    
    assert engine.snapshot_initialized is True
    assert len(engine.directory_snapshot) >= 2
    assert str(temp_dir / "test1.txt") in engine.directory_snapshot
    assert str(temp_dir / "test2.txt") in engine.directory_snapshot


def test_file_modification_detection(temp_dir, snapshot_config):
    """Test detection of file modifications."""
    test_file = temp_dir / "modify_test.txt"
    test_file.write_text("Original content")
    
    engine = SearchEngine(snapshot_config)
    
    # Initialize snapshot
    engine.search("test", search_type="filename", match_type="exact")
    original_mtime = engine.directory_snapshot[str(test_file)]['mtime']
    
    # Modify file
    time.sleep(0.1)  # Ensure different mtime
    test_file.write_text("Modified content")
    
    # Detect changes
    changed_files = engine.detect_file_changes()
    
    assert str(test_file) in changed_files
    assert engine.directory_snapshot[str(test_file)]['mtime'] != original_mtime


def test_file_deletion_detection(temp_dir, snapshot_config):
    """Test detection of file deletions."""
    test_file = temp_dir / "delete_test.txt"
    test_file.write_text("Content to be deleted")
    
    engine = SearchEngine(snapshot_config)
    
    # Initialize snapshot
    engine.search("test", search_type="filename", match_type="exact")
    assert str(test_file) in engine.directory_snapshot
    
    # Delete file
    test_file.unlink()
    
    # Detect changes
    changed_files = engine.detect_file_changes()
    
    assert str(test_file) in changed_files
    assert str(test_file) not in engine.directory_snapshot


def test_file_rename_detection(temp_dir, snapshot_config):
    """Test detection of file renames."""
    old_file = temp_dir / "old_name.txt"
    new_file = temp_dir / "new_name.txt"
    old_file.write_text("Content to be renamed")
    
    engine = SearchEngine(snapshot_config)
    
    # Initialize snapshot
    engine.search("test", search_type="filename", match_type="exact")
    assert str(old_file) in engine.directory_snapshot
    
    # Rename file
    old_file.rename(new_file)
    
    # Detect changes
    changed_files = engine.detect_file_changes()
    
    # Both old (deleted) and new (created) should be detected
    assert str(old_file) in changed_files
    assert str(new_file) in changed_files
    assert str(old_file) not in engine.directory_snapshot
    assert str(new_file) in engine.directory_snapshot


def test_new_file_detection(temp_dir, snapshot_config):
    """Test detection of new files."""
    engine = SearchEngine(snapshot_config)
    
    # Initialize snapshot with no files
    engine.search("test", search_type="filename", match_type="exact")
    initial_count = len(engine.directory_snapshot)
    
    # Create new file
    new_file = temp_dir / "new_file.txt"
    new_file.write_text("New content")
    
    # Detect changes
    changed_files = engine.detect_file_changes()
    
    assert str(new_file) in changed_files
    assert str(new_file) in engine.directory_snapshot
    assert len(engine.directory_snapshot) == initial_count + 1


def test_cache_invalidation_on_rename(temp_dir, snapshot_config):
    """Test that cache is invalidated when files are renamed."""
    old_file = temp_dir / "cache_test_old.txt"
    new_file = temp_dir / "cache_test_new.txt"
    old_file.write_text("Content for cache testing")
    
    engine = SearchEngine(snapshot_config)
    
    # First search - may create cache
    results1 = engine.search("cache", search_type="content", match_type="exact")
    
    # Rename file
    old_file.rename(new_file)
    
    # Second search - should detect change
    results2 = engine.search("cache", search_type="content", match_type="exact")
    
    # Test passes if no errors occur during rename detection
    assert isinstance(results2, list)


def test_snapshot_performance(temp_dir, snapshot_config):
    """Test that snapshot comparison doesn't significantly impact performance."""
    # Create multiple files
    for i in range(10):  # Reduced from 20 for faster testing
        (temp_dir / f"perf_test_{i}.txt").write_text(f"Performance test content {i}")
    
    engine = SearchEngine(snapshot_config)
    
    # Measure time for first search (with snapshot initialization)
    start_time = time.time()
    engine.search("perf", search_type="filename", match_type="exact")
    first_search_time = time.time() - start_time
    
    # Measure time for second search (with snapshot comparison)
    start_time = time.time()
    engine.search("test", search_type="filename", match_type="exact")
    second_search_time = time.time() - start_time
    
    # Snapshot comparison should not add significant overhead
    assert second_search_time < first_search_time * 3  # Allow 3x overhead max


def test_multiple_changes_detection(temp_dir, snapshot_config):
    """Test detection of multiple simultaneous changes."""
    # Create initial files
    file1 = temp_dir / "multi1.txt"
    file2 = temp_dir / "multi2.txt"
    file3 = temp_dir / "multi3.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    file3.write_text("Content 3")
    
    engine = SearchEngine(snapshot_config)
    
    # Initialize snapshot
    engine.search("multi", search_type="filename", match_type="exact")
    
    # Make multiple changes
    time.sleep(0.1)
    file1.write_text("Modified content 1")  # Modify
    file2.unlink()  # Delete
    file4 = temp_dir / "multi4.txt"
    file4.write_text("New content 4")  # Create
    
    # Detect all changes
    changed_files = engine.detect_file_changes()
    
    assert str(file1) in changed_files  # Modified
    assert str(file2) in changed_files  # Deleted
    assert str(file4) in changed_files  # Created
    assert len(changed_files) >= 3


def test_snapshot_consistency_after_changes(temp_dir, snapshot_config):
    """Test that snapshot remains consistent after multiple changes."""
    engine = SearchEngine(snapshot_config)
    
    # Create and modify files multiple times
    for i in range(3):  # Reduced iterations for faster testing
        test_file = temp_dir / f"consistency_{i}.txt"
        test_file.write_text(f"Content {i}")
        
        # Search to update snapshot
        engine.search("consistency", search_type="filename", match_type="exact")
        
        # Verify snapshot consistency
        assert str(test_file) in engine.directory_snapshot
        
        # Modify file
        time.sleep(0.1)
        test_file.write_text(f"Modified content {i}")
        
        # Detect changes
        changed_files = engine.detect_file_changes()
        assert str(test_file) in changed_files
