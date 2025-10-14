"""Search tool implementation for DataSage MCP server."""

import json
import time
from typing import List, Dict, Any, Optional

from ..utils.search_engine import SearchEngine
from ..utils.security import validate_search_query, SecurityError
from ..utils.resource_manager import get_resource_manager


def register_search_tool(mcp, config: Dict[str, Any]):
    """Register search tool with FastMCP server."""
    
    config_path = config.get('_config_path', 'datasage.yaml')
    search_engine = SearchEngine(config, config_path)
    max_results = config.get("tools", {}).get("search", {}).get("max_results", 50)
    tool_description = config.get("tools", {}).get("search", {}).get(
        "description", "Search files by content or filename"
    )
    resource_manager = get_resource_manager()
    
    @mcp.tool
    def search(
        query: str,
        file_type: Optional[str] = None,
        search_type: str = "both",
        match_type: Optional[str] = None,  # Will be determined based on semantic availability
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search governance documentation by content or filename.
        
        Args:
            query: Search query string
            file_type: File extension filter (e.g., ".py", ".md")
            search_type: WHERE to search:
                - "content": Search inside file contents
                - "filename": Search file/directory names only  
                - "both": Search both content and filenames (default)
            match_type: HOW to match (auto-defaults to best available):
                - "semantic": AI-powered conceptual similarity (best for understanding meaning)
                - "fuzzy": Handles typos and similar words (good for approximate matches)
                - "exact": Precise string matching (fastest, most restrictive)
                - "regex": Pattern matching with regular expressions (for advanced patterns)
            max_results: Maximum number of results to return (default: 20)
            
        Recommendations:
            - Use "semantic" match_type for conceptual queries like "data privacy compliance"
            - Use "fuzzy" for queries that might have typos
            - Use "exact" for precise technical terms
            - Use "content" search_type for document content, "filename" for file discovery
        """
        start_time = time.time()
        
        # Track request
        resource_manager.track_request()
        
        try:
            # Determine default match_type based on semantic availability
            if match_type is None:
                # Check if semantic search is enabled
                search_config = config.get("search", {})
                semantic_enabled = search_config.get("enable_semantic", False)
                match_type = "semantic" if semantic_enabled else "fuzzy"
            
            # Validate search query
            validated_query = validate_search_query(query)
            
            # Check cache with file change awareness
            cache_key = f"{validated_query}:{file_type}:{search_type}:{match_type}:{max_results}"
            
            # Validate parameters
            if search_type not in ("content", "filename", "both"):
                return _error_response(
                    "INVALID_SEARCH_TYPE", 
                    "search_type must be 'content', 'filename', or 'both'"
                )
            
            if match_type not in ("exact", "fuzzy", "regex", "semantic"):
                return _error_response(
                    "INVALID_MATCH_TYPE",
                    "match_type must be 'exact', 'fuzzy', 'regex', or 'semantic'"
                )
            
            # Limit max_results
            if max_results < 1 or max_results > max_results:
                max_results = min(max_results, max_results)
            
            # Perform search (this also detects file changes via directory snapshot)
            try:
                start_time = time.time()
                search_results = search_engine.search(
                    query=validated_query,
                    file_type=file_type,
                    search_type=search_type,
                    match_type=match_type,
                    max_results=max_results
                )
                
                # Get directory snapshot hash after search (which updates snapshot)
                snapshot_hash = hash(str(sorted(search_engine.directory_snapshot.items()))) if hasattr(search_engine, 'directory_snapshot') else 0
                cache_key_with_snapshot = f"{cache_key}:{snapshot_hash}"
                
                # Check if we have cached results for this exact snapshot
                cached_results = resource_manager.get_cached_search(cache_key_with_snapshot)
                if cached_results:
                    return cached_results
                
                # Check for search engine errors
                if search_results and isinstance(search_results[0], dict) and "error" in search_results[0]:
                    return _error_response("SEARCH_ERROR", search_results[0]["error"])
                
                # Calculate search time
                search_time_ms = (time.time() - start_time) * 1000
                
                # Prepare response data
                response_data = {
                    "query": validated_query,
                    "search_type": search_type,
                    "match_type": match_type,
                    "file_type": file_type,
                    "results": search_results,
                    "total_found": len(search_results),
                    "search_time_ms": round(search_time_ms, 2),
                    "max_results": max_results
                }
                
                # Create MCP-compliant response
                mcp_response = [
                    {
                        "type": "text",
                        "text": json.dumps(response_data, indent=2)
                    }
                ]
                
                # Cache the results with snapshot awareness
                resource_manager.cache_search_result(cache_key_with_snapshot, mcp_response)
                
                return mcp_response
                
            except Exception as e:
                return _error_response("SEARCH_ENGINE_ERROR", f"Search failed: {e}")
        
        except SecurityError as e:
            return _error_response("SECURITY_ERROR", str(e))
        
        except Exception as e:
            return _error_response("UNKNOWN_ERROR", f"Unexpected error: {e}")


def _error_response(error_code: str, message: str, details: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Create MCP-compliant error response."""
    return [
        {
            "type": "text",
            "text": json.dumps({
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details or {}
                }
            })
        }
    ]
