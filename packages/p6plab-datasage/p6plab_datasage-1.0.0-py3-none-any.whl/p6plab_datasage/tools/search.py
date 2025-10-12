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
        match_type: str = "fuzzy",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search governance documentation by content or filename.
        
        Args:
            query: Search query string
            file_type: File extension filter (e.g., ".py", ".md")
            search_type: Search scope - "content", "filename", or "both"
            match_type: Matching algorithm - "exact", "fuzzy", "regex", or "semantic"
            max_results: Maximum number of results to return
        """
        start_time = time.time()
        
        # Track request
        resource_manager.track_request()
        
        try:
            # Validate search query
            validated_query = validate_search_query(query)
            
            # Check cache first
            cache_key = f"{validated_query}:{file_type}:{search_type}:{match_type}:{max_results}"
            cached_results = resource_manager.get_cached_search(cache_key)
            if cached_results:
                return cached_results
            
            # Validate parameters
            if search_type not in ("content", "filename", "both"):
                return _error_response(
                    "INVALID_SEARCH_TYPE", 
                    "search_type must be 'content', 'filename', or 'both'"
                )
            
            if match_type not in ("exact", "fuzzy", "regex"):
                return _error_response(
                    "INVALID_MATCH_TYPE",
                    "match_type must be 'exact', 'fuzzy', or 'regex'"
                )
            
            # Limit max_results
            if max_results < 1 or max_results > max_results:
                max_results = min(max_results, max_results)
            
            # Perform search
            try:
                results = search_engine.search(
                    query=validated_query,
                    file_type=file_type,
                    search_type=search_type,
                    match_type=match_type,
                    max_results=max_results
                )
                
                # Check for search engine errors
                if results and isinstance(results[0], dict) and "error" in results[0]:
                    return _error_response("SEARCH_ERROR", results[0]["error"])
                
                # Calculate search time
                search_time_ms = (time.time() - start_time) * 1000
                
                # Prepare response data
                response_data = {
                    "query": validated_query,
                    "search_type": search_type,
                    "match_type": match_type,
                    "file_type": file_type,
                    "results": results,
                    "total_found": len(results),
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
                
                # Cache the results
                resource_manager.cache_search_result(cache_key, mcp_response)
                
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
