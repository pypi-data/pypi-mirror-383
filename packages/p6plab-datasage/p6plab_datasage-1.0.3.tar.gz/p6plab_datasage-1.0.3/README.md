# DataSage MCP Server

DataSage is a Model Context Protocol (MCP) server that provides AI assistants with secure access to local file systems. It enables generative AI tools like Amazon Q, Claude Desktop, and other MCP-compatible clients to search, read, and navigate local files and directories through a standardized interface.

## Features

- **Secure File Access**: Configurable path restrictions prevent access outside specified directories
- **Full-Text Search**: Search file contents and filenames with fuzzy matching, regex, and exact matching
- **Semantic Search**: Conceptual similarity matching using sentence embeddings with persistent caching and real-time directory snapshot comparison for comprehensive file system monitoring
- **Performance Optimization**: Built-in timing metrics, automatic cache invalidation, embedding persistence, smart caching with snapshot awareness, and real-time file system change detection
- **Directory Traversal**: Navigate directory structures with configurable depth limits
- **Text File Support**: Automatic detection and handling of text-based files with encoding support
- **Graceful Exit**: Proper signal handling (Ctrl+C) with resource cleanup
- **MCP Compliant**: Follows Model Context Protocol specification for seamless AI integration
- **FastMCP v2**: Built on the latest FastMCP framework for optimal performance

## Installation

Install DataSage using uvx (recommended):

```bash
uvx p6plab-datasage
```

Or install with pip:

```bash
pip install p6plab-datasage
```

## Quick Start

1. **Create a configuration file** (`datasage.yaml`):

```yaml
server:
  name: "My DataSage"
  description: "Local file server for AI assistants"

paths:
  - path: "~/Documents"
    description: "Personal documents"
  - path: "~/Code"
    description: "Source code files"

settings:
  max_depth: 10
  max_file_size: 10485760  # 10MB
```

2. **Start the server**:

```bash
# STDIO transport (for Claude Desktop, etc.)
uvx p6plab-datasage

# HTTP transport (for web-based clients)
uvx p6plab-datasage --transport http --port 8000

# Custom configuration
uvx p6plab-datasage --config my-config.yaml
```

## Configuration

### Configuration File Format

DataSage uses YAML configuration files with the following structure:

```yaml
server:
  name: "DataSage"                    # Server name
  description: "File server for AI"   # Server description

paths:                                # Allowed file paths
  - path: "~/Documents"
    description: "Documents folder"
  - path: "/Users/shared/projects"
    description: "Shared projects"

settings:
  max_depth: 10                       # Maximum directory depth
  max_file_size: 10485760            # Maximum file size (10MB)
  text_detection: "auto"             # Text file detection method
  excluded_extensions:               # Binary file extensions to skip
    - ".exe"
    - ".jpg"
    - ".pdf"

tools:
  search:
    description: "Search files"       # Tool descriptions
    max_results: 50
  get_page:
    description: "Get file content"
  get_page_children:
    description: "List directory contents"

search:
  fuzzy_threshold: 0.8               # Fuzzy matching threshold
  enable_regex: true                 # Enable regex search
  index_content: true                # Index file contents
  enable_semantic: true              # Enable semantic search
  semantic_model: "paraphrase-MiniLM-L3-v2"  # Lightweight model (~17MB)
```

### Environment Variables

Override configuration with environment variables (higher priority than YAML):

**Server Configuration:**
```bash
export DATASAGE_NAME="Custom DataSage"
export DATASAGE_DESCRIPTION="Custom description"
```

**Path Configuration:**
```bash
export DATASAGE_PATHS="~/Documents,~/Code,/shared/projects"
```

**Settings Configuration:**
```bash
export DATASAGE_MAX_DEPTH=5                    # Maximum directory depth (1-20)
export DATASAGE_MAX_FILE_SIZE=5242880          # Maximum file size in bytes
export DATASAGE_TEXT_DETECTION="auto"          # Text detection: "auto", "extension", "content"
export DATASAGE_EXCLUDED_EXTENSIONS=".exe,.bin,.jpg,.png"  # Comma-separated extensions
```

**Tool Configuration:**
```bash
export DATASAGE_SEARCH_MAX_RESULTS=100         # Maximum search results
export DATASAGE_TOOL_SEARCH_DESC="Search my files"
export DATASAGE_TOOL_GET_PAGE_DESC="Get file content"
export DATASAGE_TOOL_GET_PAGE_CHILDREN_DESC="List directory contents"
```

**Search Configuration:**
```bash
export DATASAGE_FUZZY_THRESHOLD=0.9            # Fuzzy matching threshold (0.0-1.0)
export DATASAGE_ENABLE_REGEX=true              # Enable regex search (true/false)
export DATASAGE_INDEX_CONTENT=true             # Index file contents (true/false)
export DATASAGE_ENABLE_SEMANTIC=true           # Enable semantic search (true/false)
export DATASAGE_SEMANTIC_MODEL="paraphrase-MiniLM-L3-v2"  # Semantic model name
```

**Complete Example:**
```bash
export DATASAGE_NAME="My Custom DataSage"
export DATASAGE_PATHS="~/Documents,~/Code"
export DATASAGE_MAX_DEPTH=5
export DATASAGE_ENABLE_SEMANTIC=true
export DATASAGE_FUZZY_THRESHOLD=0.9

uvx p6plab-datasage
```

## Available Tools

DataSage provides three MCP tools:

### 1. `search`
Search files by content or filename with multiple matching algorithms.

**Parameters:**
- `query` (required): Search query string
- `file_type` (optional): File extension filter (e.g., ".py", ".md")
- `search_type` (optional): "content", "filename", or "both" (default: "both")
- `match_type` (optional): Matching algorithm (auto-defaults to best available):
  - `semantic`: AI-powered conceptual similarity (best for understanding meaning)
  - `fuzzy`: Handles typos and similar words (good for approximate matches)
  - `exact`: Precise string matching (fastest, most restrictive)
  - `regex`: Pattern matching with regular expressions (for advanced patterns)
- `max_results` (optional): Maximum results to return (default: 20)

### 2. `get_page`
Retrieve the content of a specific file.

**Parameters:**
- `path` (required): File path to read
- `encoding` (optional): Text encoding (default: "utf-8")

### 3. `get_page_children`
List the contents of a directory with optional recursion.

**Parameters:**
- `path` (required): Directory path to list
- `max_depth` (optional): Maximum recursion depth (default: 1)
- `include_files` (optional): Include files in results (default: true)
- `include_dirs` (optional): Include directories in results (default: true)
- `file_filter` (optional): File extension filter

## Usage Examples

### With Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "datasage": {
      "command": "uvx",
      "args": ["p6plab-datasage", "--config", "/path/to/datasage.yaml"]
    }
  }
}
```

### With FastMCP Client

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("uvx p6plab-datasage") as client:
        # Search for Python files
        result = await client.call_tool("search", {
            "query": "function",
            "file_type": ".py",
            "search_type": "content"
        })
        print(result.content[0].text)
        
        # Semantic search for governance concepts
        result = await client.call_tool("search", {
            "query": "data privacy compliance",
            "search_type": "semantic",
            "max_results": 10
        })
        print(result.content[0].text)

asyncio.run(main())
```

### Command Line Options

```bash
# Basic usage
uvx p6plab-datasage

# HTTP server
uvx p6plab-datasage --transport http --port 8000

# Custom configuration
uvx p6plab-datasage --config /path/to/config.yaml

# Bind to all interfaces
uvx p6plab-datasage --transport http --host 0.0.0.0 --port 8000

# Show help
uvx p6plab-datasage --help
```

## Security

DataSage implements multiple security measures:

- **Path Validation**: Only allows access to explicitly configured paths
- **Directory Traversal Protection**: Prevents `../` attacks
- **File Type Filtering**: Automatically excludes binary files
- **Size Limits**: Configurable maximum file sizes
- **Permission Checking**: Respects file system permissions

## Development

### Running from Source

```bash
git clone <repository>
cd datasage
pip install -e .
python -m p6plab_datasage.server --config examples/datasage.yaml
```

### Building and Publishing

```bash
# Build package
./scripts/build.sh

# Publish to Test PyPI (default)
./scripts/publish.sh

# Publish to main PyPI
./scripts/publish.sh --main
```

### Running Tests

**Install test dependencies:**
```bash
pip install -e ".[dev]"
```

**Run all tests:**
```bash
# Basic test run
pytest

# Verbose output
pytest -v

# Parallel execution (recommended)
pytest -n auto

# With coverage
pytest --cov=src/p6plab_datasage

# Quick summary
pytest --tb=no -q
```

**Using UV (recommended):**
```bash
# Run all tests with parallel execution
uv run pytest tests/ -n auto -v

# Quick test run
uv run pytest tests/ --tb=no -q
```

**Test Results:**
- 26/26 tests passing (100% success rate)
- Complete coverage of all functionality
- Parallel execution with proper test isolation

### Using FastMCP CLI

```bash
fastmcp run src/p6plab_datasage/server.py
fastmcp run src/p6plab_datasage/server.py --transport http --port 8000
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
