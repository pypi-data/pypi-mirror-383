"""Tests for performance benchmarks and timing functionality."""

import time
import tempfile
import shutil
from pathlib import Path
import pytest

from p6plab_datasage.utils.search_engine import SearchEngine


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def performance_config(temp_dir):
    """Configuration for performance testing."""
    return {
        "paths": [{"path": str(temp_dir), "description": "Test files"}],
        "settings": {"max_depth": 10},
        "search": {
            "fuzzy_threshold": 0.8,
            "enable_regex": True,
            "enable_semantic": False
        }
    }


@pytest.fixture
def large_file_set(temp_dir):
    """Create a larger set of files for performance testing."""
    for i in range(10):
        filename = f"file_{i:03d}.txt"
        content = f"This is test file number {i} with content about testing and performance benchmarks."
        file_path = temp_dir / filename
        file_path.write_text(content)
    
    return temp_dir


def test_search_performance_baseline(temp_dir, large_file_set, performance_config):
    """Test performance baseline for search operations."""
    engine = SearchEngine(performance_config)
    
    start_time = time.time()
    results = engine.search("test", search_type="content", match_type="exact")
    end_time = time.time()
    
    total_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Basic performance assertion - should complete within reasonable time
    assert total_time < 3000  # 3 seconds max for 10 files
    assert isinstance(results, list)


def test_multiple_search_performance(temp_dir, large_file_set, performance_config):
    """Test performance of multiple consecutive searches."""
    engine = SearchEngine(performance_config)
    queries = ["test", "performance", "content"]
    
    for query in queries:
        start_time = time.time()
        results = engine.search(query, search_type="content", match_type="exact")
        end_time = time.time()
        
        search_time = (end_time - start_time) * 1000
        assert search_time < 2000  # 2 seconds max per search
        assert isinstance(results, list)


def test_search_result_consistency(temp_dir, large_file_set, performance_config):
    """Test that search results are consistent across multiple runs."""
    engine = SearchEngine(performance_config)
    query = "test"
    results = []
    
    # Run same search multiple times
    for _ in range(3):
        result = engine.search(query, search_type="content", match_type="exact")
        results.append(len(result))
    
    # Results should be consistent
    assert len(set(results)) <= 1  # All results should be the same count


def test_performance_with_different_match_types(temp_dir, large_file_set, performance_config):
    """Test performance across different match types."""
    engine = SearchEngine(performance_config)
    match_types = ["exact", "fuzzy"]
    query = "test"
    
    for match_type in match_types:
        start_time = time.time()
        results = engine.search(query, search_type="content", match_type=match_type)
        end_time = time.time()
        
        search_time = (end_time - start_time) * 1000
        assert search_time < 3000  # 3 seconds max
        assert isinstance(results, list)


def test_empty_result_performance(temp_dir, large_file_set, performance_config):
    """Test performance when no results are found."""
    engine = SearchEngine(performance_config)
    
    start_time = time.time()
    results = engine.search("nonexistent_unique_string_12345", search_type="content", match_type="exact")
    end_time = time.time()
    
    search_time = (end_time - start_time) * 1000
    
    # Should still complete quickly even with no results
    assert search_time < 2000  # 2 seconds max
    assert isinstance(results, list)
    assert len(results) == 0


def test_search_engine_initialization_performance(temp_dir, performance_config):
    """Test search engine initialization performance."""
    start_time = time.time()
    engine = SearchEngine(performance_config)
    end_time = time.time()
    
    init_time = (end_time - start_time) * 1000
    
    # Initialization should be fast
    assert init_time < 1000  # 1 second max
    assert engine is not None
