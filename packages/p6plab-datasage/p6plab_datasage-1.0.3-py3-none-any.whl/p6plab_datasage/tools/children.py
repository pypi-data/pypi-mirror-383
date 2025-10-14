"""Get page children tool implementation for DataSage MCP server."""

import json
from typing import List, Dict, Any, Optional

from ..config import get_allowed_paths
from ..utils.security import validate_path, SecurityError
from ..utils.file_utils import list_directory, convert_to_relative_path


def register_children_tool(mcp, config: Dict[str, Any]):
    """Register get_page_children tool with FastMCP server."""
    
    config_path = config.get('_config_path', 'datasage.yaml')
    allowed_paths = get_allowed_paths(config, config_path)
    max_depth = config.get("settings", {}).get("max_depth", 10)
    excluded_extensions = config.get("settings", {}).get("excluded_extensions", [])
    tool_description = config.get("tools", {}).get("get_page_children", {}).get(
        "description", "List directory contents"
    )
    
    @mcp.tool
    def get_page_children(
        path: str,
        max_depth: int = 1,
        include_files: bool = True,
        include_dirs: bool = True,
        file_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List governance practice directories and documents.
        
        Args:
            path: Directory path to list
            max_depth: Maximum recursion depth (1-10)
            include_files: Include files in results
            include_dirs: Include directories in results
            file_filter: File extension filter (e.g., ".py", ".md")
        """
        try:
            # Validate and resolve path
            validated_path = validate_path(path, allowed_paths)
            
            # Check if path exists and is a directory
            if not validated_path.exists():
                return _error_response("PATH_NOT_FOUND", f"Path not found: {path}")
            
            if not validated_path.is_dir():
                return _error_response("NOT_A_DIRECTORY", f"Path is not a directory: {path}")
            
            # Validate max_depth parameter
            if max_depth < 1 or max_depth > max_depth:
                return _error_response(
                    "INVALID_DEPTH", 
                    f"max_depth must be between 1 and {max_depth}"
                )
            
            # List directory contents
            try:
                children = list_directory(
                    validated_path,
                    max_depth=max_depth,
                    include_files=include_files,
                    include_dirs=include_dirs,
                    file_filter=file_filter,
                    excluded_extensions=excluded_extensions,
                    allowed_paths=allowed_paths
                )
                
                # Prepare response data
                response_data = {
                    "path": convert_to_relative_path(validated_path, allowed_paths),
                    "children": children,
                    "total_items": len(children),
                    "depth": max_depth,
                    "filters": {
                        "include_files": include_files,
                        "include_dirs": include_dirs,
                        "file_filter": file_filter
                    }
                }
                
                # Return MCP-compliant response
                return [
                    {
                        "type": "text",
                        "text": json.dumps(response_data, indent=2)
                    }
                ]
                
            except OSError as e:
                return _error_response("READ_ERROR", f"Cannot read directory: {e}")
        
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
