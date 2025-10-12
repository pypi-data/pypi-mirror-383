"""Resource management for DataSage MCP server."""

import logging
import threading
import time
from typing import Dict, Any, Set
from pathlib import Path


class ResourceManager:
    """Manage server resources and provide cleanup functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.request_count = 0
        self.search_cache = {}
        self.open_files = set()
        self.lock = threading.Lock()
        
    def track_request(self):
        """Track a new request."""
        with self.lock:
            self.request_count += 1
    
    def track_file_access(self, file_path: str):
        """Track file access for cleanup."""
        with self.lock:
            self.open_files.add(file_path)
    
    def untrack_file_access(self, file_path: str):
        """Remove file from tracking."""
        with self.lock:
            self.open_files.discard(file_path)
    
    def cache_search_result(self, query: str, results: Any):
        """Cache search results."""
        with self.lock:
            # Simple cache with size limit
            if len(self.search_cache) > 100:
                # Remove oldest entries
                oldest_keys = list(self.search_cache.keys())[:50]
                for key in oldest_keys:
                    del self.search_cache[key]
            
            self.search_cache[query] = {
                'results': results,
                'timestamp': time.time()
            }
    
    def get_cached_search(self, query: str, max_age: int = 300) -> Any:
        """Get cached search results if not expired."""
        with self.lock:
            if query in self.search_cache:
                cache_entry = self.search_cache[query]
                if time.time() - cache_entry['timestamp'] < max_age:
                    return cache_entry['results']
                else:
                    # Remove expired entry
                    del self.search_cache[query]
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics."""
        with self.lock:
            uptime = time.time() - self.start_time
            return {
                'uptime_seconds': round(uptime, 2),
                'total_requests': self.request_count,
                'cached_searches': len(self.search_cache),
                'tracked_files': len(self.open_files),
                'requests_per_second': round(self.request_count / uptime, 2) if uptime > 0 else 0
            }
    
    def cleanup(self):
        """Clean up all resources."""
        try:
            with self.lock:
                # Quick cleanup without detailed logging
                cache_size = len(self.search_cache)
                files_count = len(self.open_files)
                
                self.search_cache.clear()
                self.open_files.clear()
                
                print(f"Cleaned up {cache_size} cached searches, {files_count} file handles")
        except Exception:
            pass  # Ignore cleanup errors during shutdown


# Global instance
_resource_manager = ResourceManager()


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    return _resource_manager
