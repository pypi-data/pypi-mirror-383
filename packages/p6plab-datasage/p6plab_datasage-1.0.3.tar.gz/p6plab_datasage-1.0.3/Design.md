# DataSage MCP Server - Detailed Design

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │───▶│  DataSage MCP   │───▶│  File System    │
│ (Amazon Q, etc) │    │     Server      │    │   (Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Configuration Schema

### Configuration File Format (YAML)
```yaml
# datasage.yaml
server:
  name: "DataSage"
  description: "Local file server for AI assistants"

paths:
  - path: "/Users/docs"
    description: "Documentation files"
  - path: "/Users/code"
    description: "Source code files"

settings:
  max_depth: 10
  max_file_size: 10485760  # 10MB
  text_detection: "auto"  # "auto", "extension", "content"
  excluded_extensions:  # Binary files to explicitly exclude
    - ".exe"
    - ".bin"
    - ".jpg"
    - ".png"
    - ".pdf"
    - ".zip"
    - ".tar"
    - ".gz"

tools:
  search:
    description: "Search files by content or filename"
    max_results: 50
  get_page:
    description: "Retrieve file content"
  get_page_children:
    description: "List directory contents"

search:
  fuzzy_threshold: 0.8
  enable_regex: true
  index_content: true
  enable_semantic: true  # Enable semantic search for conceptual similarity
  semantic_model: "paraphrase-MiniLM-L3-v2"  # Lightweight model (~17MB)

# Performance & Caching Configuration
cache:
  models_dir: "~/.cache/datasage/models"      # Model storage location
  embeddings_dir: "~/.cache/datasage/embeddings"  # Persistent embedding cache
  enable_embedding_cache: true                # Enable persistent embedding cache
  cache_key_strategy: "content_hash_model"    # content_hash + model_name as key
  file_change_detection: true                 # Auto-invalidate cache when files change
  cache_invalidation: "smart_snapshot_aware"      # Use smart caching with directory snapshot comparison
  snapshot_comparison: true                   # Enable real-time file system monitoring for renames/moves/deletes
  smart_cache_keys: true                      # Include snapshot hash in cache keys for accuracy
```

### Environment Variables
**Complete configuration override support:**
```bash
# Server Configuration
DATASAGE_NAME="Custom DataSage"
DATASAGE_DESCRIPTION="Custom description"

# Path Configuration
DATASAGE_PATHS="/path1,/path2,/path3"

# Settings Configuration
DATASAGE_MAX_DEPTH=5
DATASAGE_MAX_FILE_SIZE=5242880  # 5MB in bytes
DATASAGE_TEXT_DETECTION="auto"  # "auto", "extension", "content"
DATASAGE_EXCLUDED_EXTENSIONS=".exe,.bin,.jpg,.png"  # comma-separated

# Tool Configuration
DATASAGE_SEARCH_MAX_RESULTS=100
DATASAGE_TOOL_SEARCH_DESC="Custom search description"
DATASAGE_TOOL_GET_PAGE_DESC="Custom get page description"
DATASAGE_TOOL_GET_PAGE_CHILDREN_DESC="Custom get children description"

# Search Configuration
DATASAGE_FUZZY_THRESHOLD=0.9        # 0.0-1.0
DATASAGE_ENABLE_REGEX=true          # true/false
DATASAGE_INDEX_CONTENT=true         # true/false
DATASAGE_ENABLE_SEMANTIC=true       # true/false
DATASAGE_SEMANTIC_MODEL="paraphrase-MiniLM-L3-v2"
```

## Tool Specifications

### 1. Search Tool

**Function Signature:**
```python
@mcp.tool
def search(
    query: str,
    file_type: str = None,
    search_type: str = "both",  # "content", "filename", "both", "semantic"
    match_type: str = "fuzzy",  # "exact", "fuzzy", "regex", "semantic"
    max_results: int = 20
) -> list[dict]
```

**Parameters:**
- `query` (required): Search query string
- `file_type` (optional): File extension filter (e.g., ".py", ".md")
- `search_type` (optional): Search scope - "content", "filename", or "both" (default: "both")
- `match_type` (optional): Matching algorithm - "exact", "fuzzy", "regex", or "semantic" (intelligent auto-default)
- `max_results` (optional): Maximum number of results to return

**MCP-Compliant Response Format:**
```python
# Returns list of text content items per MCP specification
return [
    {
        "type": "text",
        "text": json.dumps({
            "results": [
                {
                    "path": "/Users/docs/readme.md",
                    "filename": "readme.md",
                    "size": 1024,
                    "modified": "2024-01-15T10:30:00Z",
                    "match_type": "content",
                    "score": 0.95,
                    "snippet": "...highlighted text..."
                }
            ],
            "total_found": 15,
            "search_time_ms": 45,        # Performance benchmark timing
            "cache_hit": true,           # Embedding cache performance indicator
            "cache_invalidated": false,  # Whether cache was invalidated due to file changes
            "files_changed": 0,          # Number of files detected as changed via directory snapshot
            "snapshot_updated": true,    # Whether directory snapshot was updated
            "smart_cache_key": "query:type:match:snapshot_hash", # Smart cache key format
            "embedding_cache_size": 128  # Number of cached embeddings used
        })
    }
]
```

### 2. Get Page Tool

**Function Signature:**
```python
@mcp.tool
def get_page(
    path: str,
    encoding: str = "utf-8"
) -> list[dict]
```

**Parameters:**
- `path` (required): Absolute or relative file path
- `encoding` (optional): File encoding, defaults to utf-8

**MCP-Compliant Response Format:**
```python
# Returns text content per MCP specification
return [
    {
        "type": "text",
        "text": file_content  # Direct file content as text
    }
]
```

### 3. Get Page Children Tool

**Function Signature:**
```python
@mcp.tool
def get_page_children(
    path: str,
    max_depth: int = 1,
    include_files: bool = True,
    include_dirs: bool = True,
    file_filter: str = None
) -> list[dict]
```

**Parameters:**
- `path` (required): Directory path
- `max_depth` (optional): Maximum recursion depth (1-10)
- `include_files` (optional): Include files in results
- `include_dirs` (optional): Include directories in results
- `file_filter` (optional): File extension filter

**MCP-Compliant Response Format:**
```python
# Returns structured data as text content per MCP specification
return [
    {
        "type": "text",
        "text": json.dumps({
            "path": "/Users/docs",
            "children": [
                {
                    "name": "subfolder",
                    "path": "/Users/docs/subfolder",
                    "type": "directory",
                    "size": None,
                    "modified": "2024-01-15T10:30:00Z",
                    "children_count": 5
                },
                {
                    "name": "readme.md",
                    "path": "/Users/docs/readme.md",
                    "type": "file",
                    "size": 1024,
                    "modified": "2024-01-15T10:30:00Z",
                    "mime_type": "text/markdown"
                }
            ],
            "total_items": 2,
            "depth": 1
        })
    }
]
```

## Implementation Details

### File System Security
- Validate all paths against configured allowed paths
- Prevent directory traversal attacks (../, ..\)
- Check file permissions before access
- Sanitize file paths

### Search Implementation
- **Full-text Search**: Index file contents using simple text matching
- **Filename Search**: Pattern matching on file names
- **Semantic Search**: Conceptual similarity matching using sentence embeddings
- **Intelligent Defaults**: Automatically uses semantic matching when available, falls back to fuzzy matching
- **Fuzzy Matching**: Use Levenshtein distance with configurable threshold
- **Regex Support**: Allow regex patterns with safety limits
- **Model Caching**: Cache sentence-transformers models locally in ~/.cache/datasage/models/
- **Performance**: Lightweight paraphrase-MiniLM-L3-v2 model (17MB) for fast startup
- **Graceful Exit**: Proper signal handling and resource cleanup

### Error Handling
```python
# MCP-compliant error response format
def handle_error(error_code: str, message: str, details: dict = None):
    """Return MCP-compliant error response"""
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

# Usage in tools
@mcp.tool
def get_page(path: str) -> list[dict]:
    try:
        # ... file reading logic
        return [{"type": "text", "text": content}]
    except FileNotFoundError:
        return handle_error(
            "FILE_NOT_FOUND", 
            f"File '{path}' not found",
            {"path": path, "suggestion": "Check if the file exists"}
        )
    except PermissionError:
        return handle_error(
            "PERMISSION_DENIED",
            f"No read access to '{path}'",
            {"path": path}
        )
```

### Graceful Exit Handling
```python
import signal
import sys
import logging

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Clean up resources
    cleanup_resources()
    
    # Log shutdown
    logging.info("DataSage MCP Server shutdown complete")
    
    # Exit cleanly
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    # Windows compatibility
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)

def cleanup_resources():
    """Clean up server resources before shutdown."""
    # Close file handles
    # Clear caches
    # Log final statistics
    pass
```

**Signal Handling:**
- `SIGINT` (Ctrl+C): Interactive interrupt
- `SIGTERM`: Termination request
- `SIGBREAK`: Windows break signal (if available)

**Cleanup Process:**
1. Log shutdown initiation
2. Close open file handles
3. Clear search caches
4. Save any pending operations
5. Log final statistics
6. Exit with code 0

### Performance Considerations
- Cache file metadata for frequently accessed directories
- Implement file size limits (default 10MB)
- Use streaming for large file content
- Limit search result count to prevent memory issues

### File Type Detection
```python
# Auto-detect text files by content analysis
def is_text_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # Check for null bytes (binary indicator)
            if b'\x00' in chunk:
                return False
            # Try to decode as UTF-8
            chunk.decode('utf-8')
            return True
    except (UnicodeDecodeError, IOError):
        return False

# Common binary extensions to exclude
BINARY_EXTENSIONS = {
    '.exe', '.bin', '.dll', '.so', '.dylib',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac'
}
```

## Project Structure
```
p6plab-datasage/
├── pyproject.toml      # Package configuration and dependencies
├── README.md           # Package documentation
├── LICENSE             # Package license
├── src/
│   └── p6plab_datasage/
│       ├── __init__.py
│       ├── __main__.py     # CLI entry point
│       ├── server.py       # Main FastMCP server
│       ├── config.py       # Configuration management
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── search.py      # Search tool implementation
│       │   ├── get_page.py    # Get page tool implementation
│       │   └── children.py    # Get children tool implementation
│       └── utils/
│           ├── __init__.py
│           ├── file_utils.py  # File system utilities
│           ├── security.py    # Path validation and security
│           └── search_engine.py # Search implementation
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_config.py
│   └── test_security.py
└── examples/
    ├── datasage.yaml       # Example configuration
    └── basic_usage.py      # Usage examples
```

## Packaging Configuration

### pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "p6plab-datasage"
version = "1.0.0"
description = "MCP server for secure local file system access"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "P6P Lab", email = "contact@p6plab.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
    "pyyaml>=6.0",
    "sentence-transformers>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
p6plab-datasage = "p6plab_datasage.server:main"

[project.urls]
Homepage = "https://github.com/p6plab/datasage"
Repository = "https://github.com/p6plab/datasage"
Issues = "https://github.com/p6plab/datasage/issues"
```

### CLI Entry Point (server.py)
```python
#!/usr/bin/env python3
"""
DataSage MCP Server
Usage: 
  uvx p6plab-datasage
  uvx p6plab-datasage --transport http --port 8000
  uvx p6plab-datasage --config custom.yaml --transport http
  fastmcp run p6plab_datasage/server.py

Build & Publish:
  uv build                    # Build package
  uv publish                  # Publish to PyPI
  uv publish --index testpypi # Publish to Test PyPI
"""
import argparse
import json
from fastmcp import FastMCP
from .config import load_config
from .tools.search import register_search_tool
from .tools.get_page import register_get_page_tool
from .tools.children import register_children_tool

def create_server(config_path: str = "datasage.yaml"):
    """Create and configure DataSage MCP server"""
    config = load_config(config_path)
    
    # Create FastMCP server with configuration
    mcp = FastMCP(
        name=config.get('server', {}).get('name', 'DataSage'),
        description=config.get('server', {}).get('description', 'Local file server for AI assistants')
    )
    
    # Register tools with configuration
    register_search_tool(mcp, config)
    register_get_page_tool(mcp, config)
    register_children_tool(mcp, config)
    
    return mcp

def main():
    """Entry point for uvx execution with argument parsing"""
    parser = argparse.ArgumentParser(description='DataSage MCP Server')
    parser.add_argument('--config', '-c', default='datasage.yaml', 
                       help='Configuration file path')
    parser.add_argument('--transport', default='stdio', 
                       choices=['stdio', 'http', 'sse'],
                       help='Transport protocol')
    parser.add_argument('--host', default='127.0.0.1', 
                       help='Host to bind to (for http/sse transport)')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Port to bind to (for http/sse transport)')
    
    args = parser.parse_args()
    
    server = create_server(args.config)
    
    if args.transport == 'stdio':
        server.run()
    else:
        server.run(transport=args.transport, host=args.host, port=args.port)

# For FastMCP CLI: fastmcp run server.py
mcp = create_server()

if __name__ == '__main__':
    main()
```

### Tool Implementation Example (tools/search.py)
```python
"""Search tool implementation following MCP specification"""
import json
from typing import List, Dict, Any
from fastmcp import FastMCP
from ..utils.search_engine import SearchEngine
from ..utils.security import validate_path

def register_search_tool(mcp: FastMCP, config: dict):
    """Register search tool with FastMCP server"""
    
    search_engine = SearchEngine(config)
    
    @mcp.tool
    def search(
        query: str,
        file_type: str = None,
        search_type: str = "both",
        match_type: str = "fuzzy",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search files by content or filename.
        
        Args:
            query: Search query string
            file_type: File extension filter (e.g., ".py", ".md")
            search_type: Search scope - "content", "filename", or "both"
            match_type: Matching algorithm - "exact", "fuzzy", or "regex"
            max_results: Maximum number of results to return
        """
        try:
            results = search_engine.search(
                query=query,
                file_type=file_type,
                search_type=search_type,
                match_type=match_type,
                max_results=max_results
            )
            
            # Return MCP-compliant response
            return [
                {
                    "type": "text",
                    "text": json.dumps({
                        "results": results,
                        "total_found": len(results),
                        "query": query
                    })
                }
            ]
            
        except Exception as e:
            return [
                {
                    "type": "text",
                    "text": json.dumps({
                        "error": {
                            "code": "SEARCH_ERROR",
                            "message": str(e),
                            "details": {"query": query}
                        }
                    })
                }
            ]
```

## Development Phases

### Phase 1: Core Implementation
- Basic FastMCP server setup
- Configuration loading
- Simple file access tools
- Package structure setup

### Phase 2: Search Features
- Full-text search implementation
- Fuzzy matching
- Regex support

### Phase 3: Security & Performance
- Path validation
- File size limits
- Caching mechanisms

### Phase 4: Packaging & Distribution
- CLI entry point implementation
- PyPI package preparation with UV build system
- uvx compatibility testing
- Documentation and examples
- **Package published to PyPI as version 1.0.0**

### Phase 5: Testing & Documentation
- Comprehensive test suite
- Usage documentation
- Error handling refinement
- PyPI publication with `uv publish`
- **Complete documentation with semantic search features**

## Governance Practice Mock Data Structure

### Directory Organization
```
examples/mock-data/
├── developer-practice/
│   ├── coding-standards/
│   ├── code-review-guidelines/
│   ├── ci-cd-policies/
│   └── documentation-standards/
├── infra-practice/
│   ├── infrastructure-as-code/
│   ├── deployment-procedures/
│   ├── monitoring-guidelines/
│   └── disaster-recovery/
├── data-practice/
│   ├── data-governance/
│   ├── privacy-policies/
│   ├── data-classification/
│   └── retention-policies/
├── security-practice/
│   ├── security-policies/
│   ├── incident-response/
│   ├── access-control/
│   └── compliance-frameworks/
└── aws-practice/
    ├── well-architected/
    ├── cost-optimization/
    ├── service-guidelines/
    └── governance-frameworks/
```

### Content Categories

**Developer Practice Documents:**
- Coding standards and style guides
- Code review checklists and procedures
- CI/CD pipeline configurations
- API design guidelines
- Testing strategies and frameworks

**Infrastructure Practice Documents:**
- Infrastructure as Code templates
- Deployment runbooks and procedures
- Monitoring and alerting configurations
- Disaster recovery plans
- Capacity planning guidelines

**Data Practice Documents:**
- Data governance frameworks
- Privacy and compliance policies
- Data classification schemes
- Retention and archival policies
- Data quality standards

**Security Practice Documents:**
- Security policies and procedures
- Incident response playbooks
- Access control matrices
- Compliance checklists
- Risk assessment templates

**AWS Practice Documents:**
- Well-Architected Framework implementations
- Cost optimization strategies
- Service-specific guidelines
- Governance and compliance frameworks
- Best practice recommendations
