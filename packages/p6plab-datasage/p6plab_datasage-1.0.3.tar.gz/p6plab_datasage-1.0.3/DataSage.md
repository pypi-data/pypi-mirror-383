# DataSage

## Description
DataSage is a Model Context Protocol (MCP) server that provides AI assistants with secure access to local file systems. It enables generative AI tools like Amazon Q, Claude Desktop, and other MCP-compatible clients to search, read, and navigate local files and directories through a standardized interface.

**Key Features:**
- Secure file system access with configurable path restrictions
- Full-text and filename search capabilities with fuzzy matching
- **Semantic search using sentence-transformers for conceptual similarity matching**
- **Real-time directory snapshot comparison for comprehensive file system monitoring**
- **Smart caching solution that balances performance with accuracy**
- **Automatic detection of file renames, moves, and deletions while MCP server is running**
- **Intelligent cache invalidation with snapshot-aware cache keys**
- **Performance benchmarks and timing metrics for optimization**
- **Intelligent search defaults - automatically uses best available matching algorithm**
- Directory traversal and file content retrieval
- Support for text-based files (markdown, code, documentation)
- **Graceful exit handling with proper signal management and resource cleanup**
- Configurable descriptions and customizable tool behavior

## Tech Stack
- **Framework**: [FastMCP v2](https://github.com/jlowin/fastmcp) - Python framework for building MCP servers
- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-06-18) - Standardized protocol for AI-context integration
- **Language**: Python 3.10+
- **Configuration**: YAML + Environment Variables
- **File Handling**: Text-based files with UTF-8 encoding
- **Semantic Search**: sentence-transformers with paraphrase-MiniLM-L3-v2 model (17MB)
- **Caching**: Persistent embedding cache (~/.cache/datasage/embeddings/) with smart caching and snapshot-aware cache keys for real-time file system monitoring
- **Performance**: Built-in timing metrics and benchmarks for search operations with intelligent cache invalidation, directory snapshot comparison, and automatic performance optimization

## Requirements

### Core Functionality
- Users can override description of MCP server and each tool to match their requirements
- **Complete environment variable support for all configuration options**
- 3 tools to implement:
  - `search` - Search files by content and filename
  - `get_page` - Get file content
  - `get_page_children` - List directory contents
- Users can specify multiple paths where files are stored
- Support multiple hierarchy directories with maximum depth of 10

### Environment Variable Support
**Complete coverage of all configuration options:**
- Server configuration (name, description)
- Path configuration (comma-separated paths)
- Settings (max_depth, max_file_size, text_detection, excluded_extensions)
- Tool configuration (descriptions, max_results)
- Search configuration (fuzzy_threshold, enable_regex, index_content, enable_semantic, semantic_model)
- **Environment variables override YAML configuration**
- Support multiple hierarchy directories with maximum depth of 10

### API Specifications
- **Parameters**: Tool-specific parameters (see Design.md for details)
- **Response Format**: Follow MCP standard (https://modelcontextprotocol.io/specification/2025-06-18)
- **Pagination**: Follow MCP standard for search results

### Search Implementation
- **Search Types**: Full-text search, filename/metadata search, and semantic search
- **Semantic Search**: Conceptual similarity matching using sentence embeddings
- **Matching Algorithms**: Support exact, fuzzy, regex, and semantic matching with intelligent defaults
- **Smart Defaults**: Automatically uses semantic matching when available, falls back to fuzzy matching
- **File Types**: Text-based files only
- **Model Caching**: Local model caching in ~/.cache/datasage/models/ for performance

### Configuration
- **Sources**: Configuration file and environment variables
- **Priority**: Environment variables have higher priority than config file
- **Description Override**: Simple text format
- **Limits**: Maximum directory depth of 10 levels

### File Handling
- **Supported Types**: Text-based files only (markdown, code, txt, etc.)
- **Binary Files**: Ignore binary files
- **Security**: Restrict access to only specified paths and their children

### Error Handling
- Handle missing files, permission errors, and malformed requests transparently
- Return clear error messages to users

### Graceful Exit
- Handle SIGINT (Ctrl+C) and SIGTERM signals properly
- Clean up resources and connections before shutdown
- Log shutdown events appropriately
- Ensure no data corruption during exit

### Mock Data for Governance Practices
- Create comprehensive practice examples for senior governance teams
- Cover developer, infrastructure, data, security, and AWS practices
- Provide realistic scenarios and documentation templates
- Support AI assistant training on governance best practices
- Include policy documents, procedures, and compliance frameworks

## Packaging & Distribution

### Package Requirements
- **Package Name**: `p6plab-datasage`
- **Distribution**: **Published on PyPI** - https://pypi.org/project/p6plab-datasage/
- **Execution**: Runnable with `uvx p6plab-datasage`
- **Entry Point**: CLI command for easy server startup
- **Dependencies**: Properly declared in pyproject.toml with version constraints

### Build & Publish Scripts
- **Build**: `scripts/build.sh` - UV-based package building
- **Publish**: `scripts/publish.sh` - Direct PyPI publishing with UV (defaults to Test PyPI)
- **Commands**: `uv build` and `uv publish` for modern Python packaging
- **Status**: **Version 1.0.0 published to PyPI**