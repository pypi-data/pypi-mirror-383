"""File system utilities for text detection and metadata extraction."""

import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


# Binary extensions to exclude
BINARY_EXTENSIONS = {
    '.exe', '.bin', '.dll', '.so', '.dylib',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac', '.mkv'
}


def is_text_file(file_path: Path, max_check_size: int = 1024) -> bool:
    """
    Determine if a file is text-based by content analysis.
    
    Args:
        file_path: Path to the file
        max_check_size: Maximum bytes to check for text detection
        
    Returns:
        True if file appears to be text, False otherwise
    """
    if not file_path.exists() or not file_path.is_file():
        return False
    
    # Check file extension first
    ext = file_path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return False
    
    # Known text extensions
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
        '.xml', '.csv', '.log', '.conf', '.cfg', '.ini', '.sh', '.bat',
        '.c', '.cpp', '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs',
        '.sql', '.r', '.m', '.pl', '.ps1', '.dockerfile', '.gitignore'
    }
    
    if ext in text_extensions:
        return True
    
    # Content-based detection for files without clear extensions
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(max_check_size)
            
        # Check for null bytes (strong indicator of binary)
        if b'\x00' in chunk:
            return False
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return True
        except UnicodeDecodeError:
            # Try other common encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    chunk.decode(encoding)
                    return True
                except UnicodeDecodeError:
                    continue
            return False
            
    except (OSError, IOError):
        return False


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file metadata
    """
    try:
        stat = file_path.stat()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            if is_text_file(file_path):
                mime_type = "text/plain"
            else:
                mime_type = "application/octet-stream"
        
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "mime_type": mime_type,
            "is_text": is_text_file(file_path),
            "extension": file_path.suffix.lower()
        }
    except (OSError, IOError) as e:
        return {
            "name": file_path.name,
            "path": str(file_path),
            "error": str(e)
        }


def read_text_file(file_path: Path, max_size: int = 10485760) -> str:
    """
    Read text content from a file with encoding detection.
    
    Args:
        file_path: Path to the file
        max_size: Maximum file size to read (default 10MB)
        
    Returns:
        File content as string
        
    Raises:
        OSError: If file cannot be read
        ValueError: If file is too large or not text
    """
    if not file_path.exists():
        raise OSError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise OSError(f"Not a file: {file_path}")
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > max_size:
        raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")
    
    # Check if it's a text file
    if not is_text_file(file_path):
        raise ValueError(f"File is not text-based: {file_path}")
    
    # Try to read with different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except (OSError, IOError) as e:
            raise OSError(f"Cannot read file {file_path}: {e}")
    
    raise ValueError(f"Cannot decode file with any supported encoding: {file_path}")


def list_directory(
    dir_path: Path,
    max_depth: int = 1,
    current_depth: int = 0,
    include_files: bool = True,
    include_dirs: bool = True,
    file_filter: Optional[str] = None,
    excluded_extensions: Optional[List[str]] = None,
    allowed_paths: Optional[List[Path]] = None
) -> List[Dict[str, Any]]:
    """
    List directory contents with optional filtering and recursion.
    
    Args:
        dir_path: Directory path to list
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth
        include_files: Include files in results
        include_dirs: Include directories in results
        file_filter: File extension filter (e.g., ".py")
        excluded_extensions: List of extensions to exclude
        
    Returns:
        List of file/directory metadata dictionaries
    """
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    if current_depth >= max_depth:
        return []
    
    excluded_extensions = excluded_extensions or []
    items = []
    
    try:
        for item in sorted(dir_path.iterdir()):
            try:
                # Skip hidden files and directories
                if item.name.startswith('.'):
                    continue
                
                if item.is_file() and include_files:
                    # Apply file filter
                    if file_filter and not item.name.endswith(file_filter):
                        continue
                    
                    # Check excluded extensions
                    if item.suffix.lower() in [ext.lower() for ext in excluded_extensions]:
                        continue
                    
                    metadata = get_file_metadata(item)
                    metadata["type"] = "file"
                    
                    # Convert to relative path if allowed_paths provided
                    if allowed_paths:
                        metadata["path"] = convert_to_relative_path(item, allowed_paths)
                    
                    items.append(metadata)
                
                elif item.is_dir() and include_dirs:
                    # Get directory metadata
                    stat = item.stat()
                    dir_metadata = {
                        "name": item.name,
                        "path": convert_to_relative_path(item, allowed_paths) if allowed_paths else str(item),
                        "type": "directory",
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    }
                    
                    # Count children if not recursing further
                    if current_depth + 1 >= max_depth:
                        try:
                            children_count = len([
                                child for child in item.iterdir()
                                if not child.name.startswith('.')
                            ])
                            dir_metadata["children_count"] = children_count
                        except (OSError, PermissionError):
                            dir_metadata["children_count"] = 0
                    
                    items.append(dir_metadata)
                    
                    # Recurse into subdirectory if depth allows
                    if current_depth + 1 < max_depth:
                        children = list_directory(
                            item,
                            max_depth,
                            current_depth + 1,
                            include_files,
                            include_dirs,
                            file_filter,
                            excluded_extensions,
                            allowed_paths
                        )
                        if children:
                            dir_metadata["children"] = children
                            
            except (OSError, PermissionError):
                # Skip items we can't access
                continue
                
    except (OSError, PermissionError):
        # Return empty list if we can't read the directory
        return []
    
    return items


def get_file_snippet(file_path: Path, query: str, context_lines: int = 2) -> Optional[str]:
    """
    Get a snippet of text around a search match.
    
    Args:
        file_path: Path to the file
        query: Search query to find
        context_lines: Number of lines of context around match
        
    Returns:
        Text snippet with highlighted match, or None if not found
    """
    try:
        content = read_text_file(file_path)
        lines = content.split('\n')
        
        # Find lines containing the query
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # Get context lines
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                
                snippet_lines = lines[start:end]
                snippet = '\n'.join(snippet_lines)
                
                # Highlight the match (simple approach)
                highlighted = snippet.replace(
                    query, f"**{query}**"
                ).replace(
                    query.lower(), f"**{query.lower()}**"
                ).replace(
                    query.upper(), f"**{query.upper()}**"
                )
                
                return highlighted
                
    except (OSError, ValueError):
        pass
    
    return None

def convert_to_relative_path(file_path: Path, allowed_paths: List[Path]) -> str:
    """Convert absolute path to relative path with disambiguation."""
    for base_path in allowed_paths:
        try:
            rel_path = file_path.relative_to(base_path)
            if len(allowed_paths) > 1:
                # Check if base directory names are unique
                base_names = [p.name for p in allowed_paths]
                if len(set(base_names)) == len(base_names):
                    # All base names are unique, use just the base name
                    return f"{base_path.name}/{rel_path}"
                else:
                    # Base names have duplicates, use more parent context
                    parent_parts = base_path.parts[-2:] if len(base_path.parts) >= 2 else base_path.parts
                    prefix = "/".join(parent_parts)
                    return f"{prefix}/{rel_path}"
            else:
                return str(rel_path)
        except ValueError:
            continue
    return str(file_path)
