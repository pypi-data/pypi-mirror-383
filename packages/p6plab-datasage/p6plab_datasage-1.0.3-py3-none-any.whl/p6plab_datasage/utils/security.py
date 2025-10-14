"""Security utilities for path validation and access control."""

import os
from pathlib import Path
from typing import List, Optional


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


def validate_path(path: str, allowed_paths: List[Path]) -> Path:
    """
    Validate that a path is safe and within allowed directories.
    
    Args:
        path: Path to validate
        allowed_paths: List of allowed root paths
        
    Returns:
        Resolved Path object if valid
        
    Raises:
        SecurityError: If path is invalid or not allowed
    """
    if not path:
        raise SecurityError("Empty path not allowed")
    
    # Convert to Path and resolve
    try:
        # Handle relative paths by resolving against allowed paths
        input_path = Path(path)
        
        # If it's a relative path, try to resolve it against each allowed path
        if not input_path.is_absolute():
            for allowed_path in allowed_paths:
                try:
                    candidate_path = (allowed_path / path).resolve()
                    if candidate_path.exists() or candidate_path.parent.exists():
                        resolved_path = candidate_path
                        break
                except (OSError, ValueError):
                    continue
            else:
                # If no match found, resolve normally
                resolved_path = input_path.expanduser().resolve()
        else:
            resolved_path = input_path.expanduser().resolve()
            
    except (OSError, ValueError) as e:
        raise SecurityError(f"Invalid path: {e}")
    
    # Check for directory traversal attempts in original path
    if ".." in path and not any(str(resolved_path).startswith(str(allowed)) for allowed in allowed_paths):
        raise SecurityError("Directory traversal not allowed")
    
    # Sanitize path components
    path_parts = resolved_path.parts
    for part in path_parts:
        if "\x00" in part:
            raise SecurityError(f"Invalid path component: {part}")
    
    # Check if path is within allowed directories
    if not _is_path_allowed(resolved_path, allowed_paths):
        raise SecurityError(f"Path not in allowed directories: {resolved_path}")
    
    return resolved_path


def _is_path_allowed(path: Path, allowed_paths: List[Path]) -> bool:
    """Check if path is within any of the allowed directories."""
    if not allowed_paths:
        return False
    
    for allowed_path in allowed_paths:
        try:
            # Check if path is under allowed_path
            path.relative_to(allowed_path)
            return True
        except ValueError:
            # path is not under allowed_path
            continue
    
    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove null bytes and control characters
    sanitized = "".join(c for c in filename if ord(c) >= 32 and c != "\x7f")
    
    # Remove dangerous characters
    dangerous_chars = '<>:"|?*\\'
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "_")
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # Ensure it's not empty after sanitization
    if not sanitized.strip():
        return "unnamed"
    
    return sanitized.strip()


def check_file_permissions(path: Path) -> bool:
    """
    Check if file is readable.
    
    Args:
        path: Path to check
        
    Returns:
        True if readable, False otherwise
    """
    try:
        return os.access(path, os.R_OK)
    except (OSError, ValueError):
        return False


def is_safe_symlink(path: Path, allowed_paths: List[Path]) -> bool:
    """
    Check if symlink target is safe and within allowed paths.
    
    Args:
        path: Symlink path to check
        allowed_paths: List of allowed root paths
        
    Returns:
        True if symlink is safe, False otherwise
    """
    if not path.is_symlink():
        return True
    
    try:
        target = path.resolve()
        return _is_path_allowed(target, allowed_paths)
    except (OSError, ValueError):
        return False


def get_safe_relative_path(path: Path, base_path: Path) -> Optional[str]:
    """
    Get relative path safely, returning None if path is outside base.
    
    Args:
        path: Path to make relative
        base_path: Base path to make relative to
        
    Returns:
        Relative path string or None if unsafe
    """
    try:
        relative = path.relative_to(base_path)
        # Check for upward traversal in result
        if ".." in str(relative):
            return None
        return str(relative)
    except ValueError:
        return None


def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query.
    
    Args:
        query: Search query to validate
        
    Returns:
        Sanitized query
        
    Raises:
        SecurityError: If query is invalid
    """
    if not query or not query.strip():
        raise SecurityError("Empty search query")
    
    # Limit query length
    if len(query) > 1000:
        raise SecurityError("Search query too long")
    
    # Remove null bytes and control characters
    sanitized = "".join(c for c in query if ord(c) >= 32 or c in "\t\n\r")
    
    if not sanitized.strip():
        raise SecurityError("Invalid search query")
    
    return sanitized.strip()


def validate_file_extension(filename: str, excluded_extensions: List[str]) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Filename to check
        excluded_extensions: List of excluded extensions
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension
    ext = Path(filename).suffix.lower()
    
    # Check against excluded extensions
    return ext not in [e.lower() for e in excluded_extensions]
