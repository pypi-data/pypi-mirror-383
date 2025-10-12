# DataSage

## Description
DataSage is a Model Context Protocol (MCP) server that provides AI assistants with secure access to local file systems. It enables generative AI tools like Amazon Q, Claude Desktop, and other MCP-compatible clients to search, read, and navigate local files and directories through a standardized interface.

**Key Features:**
- Secure file system access with configurable path restrictions
- Full-text and filename search capabilities with fuzzy matching
- **Semantic search using sentence-transformers for conceptual similarity matching**
- Directory traversal and file content retrieval
- Support for text-based files (markdown, code, documentation)
- Configurable descriptions and customizable tool behavior

## Tech Stack
- **Framework**: [FastMCP v2](https://github.com/jlowin/fastmcp) - Python framework for building MCP servers
- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-06-18) - Standardized protocol for AI-context integration
- **Language**: Python 3.10+
- **Configuration**: YAML + Environment Variables
- **File Handling**: Text-based files with UTF-8 encoding
- **Semantic Search**: sentence-transformers with paraphrase-MiniLM-L3-v2 model (17MB)

## Requirements

### Core Functionality
- Users can override description of MCP server and each tool to match their requirements
- 3 tools to implement:
  - `search` - Search files by content and filename
  - `get_page` - Get file content
  - `get_page_children` - List directory contents
- Users can specify multiple paths where files are stored
- Support multiple hierarchy directories with maximum depth of 10

### API Specifications
- **Parameters**: Tool-specific parameters (see Design.md for details)
- **Response Format**: Follow MCP standard (https://modelcontextprotocol.io/specification/2025-06-18)
- **Pagination**: Follow MCP standard for search results

### Search Implementation
- **Search Types**: Full-text search, filename/metadata search, and semantic search
- **Semantic Search**: Conceptual similarity matching using sentence embeddings
- **Matching**: Support regex, fuzzy matching, exact matches, and cosine similarity
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
- **Distribution**: Ready for PyPI publication
- **Execution**: Must be runnable with `uvx p6plab-datasage`
- **Entry Point**: Provide CLI command for easy server startup
- **Dependencies**: Properly declared in pyproject.toml with version constraints

### Build & Publish Scripts
- **Build**: `scripts/build-and-publish.sh` - UV-based package building
- **Publish**: `scripts/publish.sh` - Direct PyPI publishing with UV
- **Commands**: `uv build` and `uv publish` for modern Python packaging