"""Get page tool implementation for DataSage MCP server."""

import json
from typing import List, Dict, Any
from pathlib import Path

from ..config import get_allowed_paths
from ..utils.security import validate_path, SecurityError
from ..utils.file_utils import read_text_file, get_file_metadata
from ..utils.resource_manager import get_resource_manager


def register_get_page_tool(mcp, config: Dict[str, Any]):
    """Register get_page tool with FastMCP server."""
    
    config_path = config.get('_config_path', 'datasage.yaml')
    allowed_paths = get_allowed_paths(config, config_path)
    max_file_size = config.get("settings", {}).get("max_file_size", 10485760)
    tool_description = config.get("tools", {}).get("get_page", {}).get(
        "description", "Retrieve file content"
    )
    resource_manager = get_resource_manager()
    
    @mcp.tool
    def get_page(
        path: str,
        encoding: str = "utf-8"
    ) -> List[Dict[str, Any]]:
        """Retrieve governance document content.
        
        Args:
            path: File path to read (absolute or relative to configured paths)
            encoding: Text encoding to use (default: utf-8)
        """
        # Track request
        resource_manager.track_request()
        
        try:
            # Validate and resolve path
            validated_path = validate_path(path, allowed_paths)
            
            # Track file access
            resource_manager.track_file_access(str(validated_path))
            
            try:
                # Check if file exists and is readable
                if not validated_path.exists():
                    return _error_response("FILE_NOT_FOUND", f"File not found: {path}")
                
                if not validated_path.is_file():
                    return _error_response("NOT_A_FILE", f"Path is not a file: {path}")
                
                # Read file content
                try:
                    content = read_text_file(validated_path, max_file_size)
                    
                    # Return MCP-compliant response with file content
                    return [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                    
                except ValueError as e:
                    if "too large" in str(e).lower():
                        return _error_response("FILE_TOO_LARGE", str(e))
                    elif "not text-based" in str(e).lower():
                        return _error_response("NOT_TEXT_FILE", str(e))
                    else:
                        return _error_response("INVALID_FILE", str(e))
                
                except OSError as e:
                    return _error_response("READ_ERROR", f"Cannot read file: {e}")
            
            finally:
                # Untrack file access
                resource_manager.untrack_file_access(str(validated_path))
        
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
