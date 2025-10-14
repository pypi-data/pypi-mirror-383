# Changelog

All notable changes to DataSage MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-10-13

### Added
- **Directory Snapshot Comparison**: Real-time file system change detection for comprehensive monitoring
- **Smart Caching Solution**: Snapshot-aware cache keys that balance performance with accuracy
- **Enhanced File System Monitoring**: Detects file renames, moves, and deletions automatically
- **Intelligent Cache Invalidation**: Automatic cache expiration when file system changes occur
- **Comprehensive Test Suite**: 9 new tests for directory snapshot functionality (60 total tests)

### Changed
- **MCP Tool Caching**: Enhanced to include directory snapshot hash in cache keys
- **Search Performance**: Maintains fast response times while ensuring real-time accuracy
- **Cache Management**: Improved cache lifecycle management with automatic cleanup

### Fixed
- **File Rename Detection**: Files renamed while MCP server is running now show correct names immediately
- **Deleted File Handling**: Removed files no longer appear in search results
- **Cache Staleness**: Eliminated stale search results when file system changes occur
- **Variable Name Issues**: Fixed search tool variable references for proper error handling

### Performance
- **Smart Caching**: Cache hits provide same performance as before (~1-5ms)
- **Change Detection**: File system monitoring adds minimal overhead (~1-10ms)
- **Real-time Updates**: Immediate reflection of file system changes in search results
- **Automatic Optimization**: Cache automatically expires only when necessary

## [1.0.2] - 2025-10-13

### Added
- Intelligent file-change detection for embedding cache invalidation
- Automatic cache cleanup when source files are modified
- Enhanced cache validation using file modification time (mtime)
- Proper model name extraction for cache file naming (fixes "unknown" model names)

### Changed
- Improved embedding cache key generation with correct model names
- Enhanced cache file naming convention for better identification

### Fixed
- Fixed cache file naming to use actual model names instead of "unknown"
- Improved cache invalidation logic to handle file modifications properly

### Performance
- Intelligent cache management ensures embeddings are always fresh
- Automatic cleanup of stale cache files when source files change
- Maintains 10x+ performance benefits while ensuring data accuracy

## [1.0.1] - 2025-10-12

### Added
- Intelligent search defaults - automatically uses semantic matching when available
- Comprehensive environment variable support for all configuration options
- Enhanced AI agent documentation with detailed match_type descriptions
- Persistent embedding cache to ~/.cache/datasage/embeddings/ for improved performance
- Performance benchmarks for search operations
- pytest-xdist for better test isolation

### Changed
- Simplified search logic - clear separation of search_type (WHERE) vs match_type (HOW)
- Removed semantic from search_type options to reduce confusion
- Enhanced search tool docstring with usage recommendations
- Updated all documentation to reflect intelligent defaults

### Fixed
- Fixed semantic search validation in search tool
- Fixed syntax error in search engine (continue statement)
- Fixed test isolation issues with environment variables
- Added missing semantic search defaults to configuration

### Performance
- Added persistent embedding cache for faster subsequent searches
- Intelligent match_type defaults reduce configuration overhead
- Model caching prevents re-downloading on each startup

## [1.0.0] - 2025-10-11

### Added
- Initial release of DataSage MCP Server
- Secure file system access with configurable path restrictions
- Full-text and filename search with fuzzy matching
- Semantic search using sentence-transformers
- Directory traversal and file content retrieval
- Graceful exit handling with proper signal management
- FastMCP v2 integration with MCP compliance
- Comprehensive governance practice mock data (18 documents)
- UV-based build and publish system
- Complete test suite with 100% pass rate

### Features
- 3 MCP tools: search, get_page, get_page_children
- Multiple search types: content, filename, both
- Multiple match types: exact, fuzzy, regex, semantic
- YAML + environment variable configuration
- Cross-platform signal handling (SIGINT, SIGTERM, SIGBREAK)
- Resource management and cleanup
- Text file detection and encoding support
- Path validation and security protection

### Documentation
- Complete README with usage examples
- Detailed design documentation
- Development task tracking
- API specifications and examples
- Configuration guide with environment variables

### Deployment
- Published on PyPI as p6plab-datasage
- uvx compatible for easy installation
- Multiple transport modes (stdio, http, sse)
- Docker-ready configuration
- Example configurations for different use cases
