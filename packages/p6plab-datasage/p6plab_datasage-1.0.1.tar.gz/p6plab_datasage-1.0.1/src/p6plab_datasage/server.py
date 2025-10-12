#!/usr/bin/env python3
"""
DataSage MCP Server
Usage: 
  uvx p6plab-datasage
  uvx p6plab-datasage --transport http --port 8000
  uvx p6plab-datasage --config custom.yaml --transport http
  fastmcp run p6plab_datasage/server.py
"""

import argparse
import sys
import logging
from pathlib import Path

from fastmcp import FastMCP

from .config import load_config
from .tools.search import register_search_tool
from .tools.get_page import register_get_page_tool
from .tools.children import register_children_tool
from .utils.graceful_exit import setup_graceful_exit, add_cleanup_callback
from .utils.resource_manager import get_resource_manager


def setup_logging():
    """Setup logging for the server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def create_server(config_path: str = "datasage.yaml") -> FastMCP:
    """Create and configure DataSage MCP server."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = load_config(config_path)
        config['_config_path'] = config_path  # Store config path for tools
        
        # Create FastMCP server with configuration
        mcp = FastMCP(
            name=config.get('server', {}).get('name', 'DataSage')
        )
        
        # Get resource manager
        resource_manager = get_resource_manager()
        
        # Register tools with configuration
        register_search_tool(mcp, config)
        register_get_page_tool(mcp, config)
        register_children_tool(mcp, config)
        
        # Setup graceful exit handling
        graceful_exit = setup_graceful_exit()
        add_cleanup_callback(resource_manager.cleanup)
        
        logger.info("DataSage MCP Server initialized successfully")
        
        # Print startup information
        allowed_paths = config.get("paths", [])
        if allowed_paths:
            logger.info(f"DataSage MCP Server configured with {len(allowed_paths)} path(s):")
            for path_config in allowed_paths:
                if isinstance(path_config, str):
                    path_str = path_config
                else:
                    path_str = path_config.get("path", "")
                
                resolved_path = Path(path_str).expanduser().resolve()
                status = "✓" if resolved_path.exists() else "✗"
                logger.info(f"  {status} {resolved_path}")
        else:
            logger.warning("No paths configured. Server will have limited functionality.")
        
        return mcp
        
    except Exception as e:
        print(f"Error creating server: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Entry point for uvx execution with argument parsing."""
    parser = argparse.ArgumentParser(
        description='DataSage MCP Server - Secure local file system access for AI assistants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Start with stdio transport
  %(prog)s --transport http --port 8000      # Start HTTP server on port 8000
  %(prog)s --config custom.yaml              # Use custom configuration
  %(prog)s --transport http --host 0.0.0.0   # Bind to all interfaces
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='datasage.yaml',
        help='Configuration file path (default: datasage.yaml)'
    )
    parser.add_argument(
        '--transport', 
        default='stdio',
        choices=['stdio', 'http', 'sse'],
        help='Transport protocol (default: stdio)'
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to for http/sse transport (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='Port to bind to for http/sse transport (default: 8000)'
    )
    parser.add_argument(
        '--version', 
        action='version',
        version='DataSage MCP Server 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create server
    server = create_server(args.config)
    logger = logging.getLogger(__name__)
    
    # Start server with appropriate transport
    try:
        if args.transport == 'stdio':
            logger.info("Starting DataSage MCP Server with stdio transport...")
            server.run()
        else:
            logger.info(f"Starting DataSage MCP Server with {args.transport} transport on {args.host}:{args.port}...")
            server.run(transport=args.transport, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


# For FastMCP CLI: fastmcp run server.py
# This creates a server instance that the CLI can discover and run
def _create_default_server():
    """Create default server for FastMCP CLI discovery."""
    try:
        return create_server()
    except Exception:
        # If configuration fails during import, create a minimal server
        # This allows the CLI to still discover the server
        return FastMCP("DataSage")

# Only create the server when accessed, not during import
import sys
if 'pytest' not in sys.modules:
    mcp = _create_default_server()
else:
    # During testing, create a minimal server to avoid side effects
    mcp = FastMCP("DataSage")


if __name__ == '__main__':
    main()
