"""Search engine for file content and filename searching."""

import re
import time
import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .file_utils import is_text_file, read_text_file, get_file_metadata, get_file_snippet

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match_score(query: str, text: str, threshold: float = 0.8) -> float:
    """
    Calculate fuzzy match score between query and text.
    
    Args:
        query: Search query
        text: Text to match against
        threshold: Minimum similarity threshold
        
    Returns:
        Match score between 0.0 and 1.0, or 0.0 if below threshold
    """
    if not query or not text:
        return 0.0
    
    query_lower = query.lower()
    text_lower = text.lower()
    
    # Exact match gets highest score
    if query_lower == text_lower:
        return 1.0
    
    # Substring match gets high score
    if query_lower in text_lower:
        return 0.9
    
    # Calculate Levenshtein distance
    distance = levenshtein_distance(query_lower, text_lower)
    max_len = max(len(query_lower), len(text_lower))
    
    if max_len == 0:
        return 0.0
    
    similarity = 1.0 - (distance / max_len)
    
    return similarity if similarity >= threshold else 0.0


class SearchEngine:
    """File search engine with multiple search modes."""
    
    def __init__(self, config: Dict[str, Any], config_path: str = "datasage.yaml"):
        """Initialize search engine with configuration."""
        from ..config import get_allowed_paths
        
        self.config = config
        self.allowed_paths = get_allowed_paths(config, config_path)
        
        # Search settings
        search_config = config.get("search", {})
        self.fuzzy_threshold = search_config.get("fuzzy_threshold", 0.8)
        self.enable_regex = search_config.get("enable_regex", True)
        self.max_file_size = config.get("settings", {}).get("max_file_size", 10485760)
        self.excluded_extensions = config.get("settings", {}).get("excluded_extensions", [])
        
        # Semantic search setup
        self.semantic_enabled = SEMANTIC_SEARCH_AVAILABLE and search_config.get("enable_semantic", False)
        self.model = None
        self.embeddings_cache = {}
        
        # Initialize directory snapshot for comprehensive change detection
        self.directory_snapshot = {}
        self.snapshot_initialized = False
        
        if self.semantic_enabled:
            try:
                model_name = search_config.get("semantic_model", "all-MiniLM-L6-v2")
                self.semantic_model_name = model_name
                # Cache model locally to avoid redownloading
                cache_dir = Path.home() / ".cache" / "datasage" / "models"
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                # Setup embedding cache directory
                self.embedding_cache_dir = Path.home() / ".cache" / "datasage" / "embeddings"
                self.embedding_cache_dir.mkdir(parents=True, exist_ok=True)
                
                self.model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
            except Exception:
                self.semantic_enabled = False
    
    def update_directory_snapshot(self):
        """Update directory snapshot with current file states."""
        new_snapshot = {}
        
        for allowed_path in self.allowed_paths:
            if allowed_path.exists():
                for file_path in self._walk_directory(allowed_path):
                    try:
                        stat = file_path.stat()
                        new_snapshot[str(file_path)] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except (OSError, PermissionError):
                        continue
        
        return new_snapshot

    def detect_file_changes(self):
        """Detect file system changes and invalidate affected cache entries."""
        current_snapshot = self.update_directory_snapshot()
        
        if not self.snapshot_initialized:
            self.directory_snapshot = current_snapshot
            self.snapshot_initialized = True
            return []
        
        changed_files = []
        
        # Check for modified or new files
        for file_path, file_info in current_snapshot.items():
            old_info = self.directory_snapshot.get(file_path)
            if not old_info or old_info['mtime'] != file_info['mtime']:
                changed_files.append(file_path)
        
        # Check for deleted files
        for file_path in self.directory_snapshot:
            if file_path not in current_snapshot:
                changed_files.append(file_path)
                # Remove cache for deleted files
                self._invalidate_cache_for_file(file_path)
        
        # Update snapshot
        self.directory_snapshot = current_snapshot
        
        # Invalidate cache for changed files
        for file_path in changed_files:
            self._invalidate_cache_for_file(file_path)
        
        return changed_files

    def _invalidate_cache_for_file(self, file_path):
        """Invalidate cache entries for a specific file."""
        if not hasattr(self, 'embedding_cache_dir') or not self.embedding_cache_dir.exists():
            return
        
        file_name = Path(file_path).name
        # Remove all cache files that start with this filename
        pattern = f"{file_name}_*"
        for cache_file in self.embedding_cache_dir.glob(pattern):
            cache_file.unlink(missing_ok=True)

    def cleanup_orphaned_cache(self):
        """Remove cache files for deleted source files (legacy method)."""
        # This method is now supplemented by directory snapshot comparison
        pass

    def search(
        self,
        query: str,
        file_type: Optional[str] = None,
        search_type: str = "both",
        match_type: str = "fuzzy",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for files matching the query.
        
        Args:
            query: Search query
            file_type: File extension filter (e.g., ".py")
            search_type: WHERE to search - "content", "filename", or "both"
            match_type: HOW to match - "exact", "fuzzy", "regex", or "semantic"
            max_results: Maximum number of results
            
        Returns:
            List of search results with metadata and scores
        """
        # Detect file system changes and update cache accordingly
        changed_files = self.detect_file_changes()
            
        start_time = time.time()
        results = []
        
        if not query.strip():
            return results
        
        # Validate regex if using regex search
            return results
        
        # Validate regex if using regex search
        if match_type == "regex" and self.enable_regex:
            try:
                re.compile(query)
            except re.error:
                return [{
                    "error": "Invalid regex pattern",
                    "query": query
                }]
        
        # Search in all allowed paths
        for base_path in self.allowed_paths:
            path_results = self._search_in_path(
                base_path, query, file_type, search_type, match_type, max_results - len(results)
            )
            results.extend(path_results)
            
            if len(results) >= max_results:
                break
        
        # Sort results by score (descending)
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        # Limit results
        results = results[:max_results]
        
        # Add search metadata
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return results
    
    def _search_in_path(
        self,
        base_path: Path,
        query: str,
        file_type: Optional[str],
        search_type: str,
        match_type: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search for files in a specific path."""
        results = []
        
        try:
            for file_path in self._walk_directory(base_path):
                if len(results) >= max_results:
                    break
                
                # Apply file type filter
                if file_type and not file_path.name.endswith(file_type):
                    continue
                
                # Check excluded extensions
                if file_path.suffix.lower() in [ext.lower() for ext in self.excluded_extensions]:
                    continue
                
                # Only search text files for content
                if search_type in ("content", "both") and not is_text_file(file_path):
                    if search_type == "content":
                        continue
                
                # Perform search
                result = self._search_file(file_path, query, search_type, match_type)
                if result and result.get("score", 0) > 0:
                    results.append(result)
        
        except (OSError, PermissionError):
            pass
        
        return results
    
    def _walk_directory(self, path: Path) -> List[Path]:
        """Walk directory and return all files."""
        files = []
        max_depth = self.config.get("settings", {}).get("max_depth", 10)
        
        def _walk_recursive(current_path: Path, depth: int = 0):
            if depth >= max_depth:
                return
            
            try:
                for item in current_path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        files.append(item)
                    elif item.is_dir():
                        _walk_recursive(item, depth + 1)
            except (OSError, PermissionError):
                pass
        
        _walk_recursive(path)
        return files
    
    def _search_file(
        self,
        file_path: Path,
        query: str,
        search_type: str,
        match_type: str
    ) -> Optional[Dict[str, Any]]:
        """Search within a single file."""
        try:
            # Get file metadata
            metadata = get_file_metadata(file_path)
            
            # Convert to relative path with disambiguation for multiple paths
            relative_path = str(file_path)
            for base_path in self.allowed_paths:
                try:
                    rel_path = file_path.relative_to(base_path)
                    if len(self.allowed_paths) > 1:
                        # Check if base directory names are unique
                        base_names = [p.name for p in self.allowed_paths]
                        if len(set(base_names)) == len(base_names):
                            # All base names are unique, use just the base name
                            relative_path = f"{base_path.name}/{rel_path}"
                        else:
                            # Base names have duplicates, use more parent context
                            # Use last 2 parts of the base path for disambiguation
                            parent_parts = base_path.parts[-2:] if len(base_path.parts) >= 2 else base_path.parts
                            prefix = "/".join(parent_parts)
                            relative_path = f"{prefix}/{rel_path}"
                    else:
                        relative_path = str(rel_path)
                    break
                except ValueError:
                    continue
            
            result = {
                "path": relative_path,
                "filename": file_path.name,
                "size": metadata.get("size", 0),
                "modified": metadata.get("modified", ""),
                "mime_type": metadata.get("mime_type", ""),
                "score": 0.0,
                "match_type": "",
                "snippet": ""
            }
            
            filename_score = 0.0
            content_score = 0.0
            
            # Search filename
            if search_type in ("filename", "both"):
                filename_score = self._match_text(file_path.name, query, match_type)
                if filename_score > 0:
                    result["match_type"] = "filename"
                    result["score"] = filename_score
            
            # Search content
            if search_type in ("content", "both") and is_text_file(file_path):
                try:
                    content = read_text_file(file_path, self.max_file_size)
                    
                    if match_type == "semantic":
                        if not self.semantic_enabled:
                            content_score = 0.0  # No semantic search available
                        else:
                            content_score = self._semantic_search(query, file_path, content)
                    else:
                        content_score = self._match_text(content, query, match_type)
                    
                    if content_score > 0:
                        if content_score > filename_score:
                            result["match_type"] = "content" if match_type != "semantic" else "semantic"
                            result["score"] = content_score
                        
                        # Get snippet for content matches
                        snippet = get_file_snippet(file_path, query, context_lines=2)
                        if snippet:
                            result["snippet"] = snippet
                
                except (OSError, ValueError):
                    # Skip files we can't read
                    pass
            
            # Return result if we found a match
            if result["score"] > 0:
                return result
            
        except (OSError, PermissionError):
            pass
        
        return None
    
    def _match_text(self, text: str, query: str, match_type: str) -> float:
        """Match text against query using specified match type."""
        if not text or not query:
            return 0.0
        
        if match_type == "exact":
            return 1.0 if query.lower() in text.lower() else 0.0
        
        elif match_type == "fuzzy":
            # For long text, check if query appears as substring first
            if query.lower() in text.lower():
                return 0.9
            
            # For filename matching, use fuzzy matching
            if len(text) < 200:  # Only fuzzy match short text
                return fuzzy_match_score(query, text, self.fuzzy_threshold)
            else:
                # For long content, split into words and check fuzzy match
                words = text.lower().split()
                best_score = 0.0
                for word in words:
                    score = fuzzy_match_score(query, word, self.fuzzy_threshold)
                    best_score = max(best_score, score)
                return best_score
        
        elif match_type == "regex" and self.enable_regex:
            try:
                pattern = re.compile(query, re.IGNORECASE)
                matches = pattern.findall(text)
                return 1.0 if matches else 0.0
            except re.error:
                return 0.0
        
        return 0.0

    def _semantic_search(self, query: str, file_path: Path, content: str) -> float:
        """Perform semantic similarity search using embeddings."""
        if not self.semantic_enabled or not self.model:
            return 0.0
        
        try:
            # Create cache key based on file path, content hash, and model
            content_hash = hashlib.md5(content.encode()).hexdigest()
            model_name = getattr(self, 'semantic_model_name', 'unknown').replace('/', '_').replace('-', '_')
            cache_key = f"{file_path.name}_{content_hash}_{model_name}"
            cache_file = self.embedding_cache_dir / f"{cache_key}.pkl"
            
            # Check if file has changed since cache creation
            file_mtime = file_path.stat().st_mtime
            cache_valid = cache_file.exists()
            if cache_valid:
                cache_mtime = cache_file.stat().st_mtime
                if file_mtime > cache_mtime:
                    # File changed after cache - invalidate
                    cache_file.unlink(missing_ok=True)
                    cache_valid = False
            
            # Try to load cached embedding
            content_embedding = None
            if cache_valid:
                try:
                    with open(cache_file, 'rb') as f:
                        content_embedding = pickle.load(f)
                except (pickle.PickleError, EOFError):
                    # Cache file corrupted, will regenerate
                    cache_file.unlink(missing_ok=True)
            
            # Generate embedding if not cached
            if content_embedding is None:
                # Use first 1000 chars for embedding to avoid memory issues
                text_sample = content[:1000]
                content_embedding = self.model.encode(text_sample)
                
                # Save to persistent cache
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(content_embedding, f)
                except (OSError, pickle.PickleError):
                    # Cache write failed, continue without caching
                    pass
            
            # Store in memory cache for this session
            memory_cache_key = f"{file_path}:{content_hash}"
            self.embeddings_cache[memory_cache_key] = content_embedding
            
            # Get query embedding
            query_embedding = self.model.encode(query)
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, content_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
            )
            
            return float(similarity)
        except Exception:
            return 0.0
