#!/usr/bin/env python3
"""
Basic usage example for DataSage MCP server.

This example shows how to:
1. Create a DataSage server programmatically
2. Use the FastMCP client to interact with it
3. Call the available tools (search, get_page, get_page_children)
"""

import asyncio
import tempfile
from pathlib import Path

from fastmcp import Client
from p6plab_datasage.server import create_server


async def main():
    """Demonstrate basic DataSage usage."""
    
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "readme.md").write_text("""
# Test Project

This is a test project for demonstrating DataSage.

## Features
- File search
- Content retrieval
- Directory listing
""")
        
        (temp_path / "main.py").write_text("""
#!/usr/bin/env python3
\"\"\"Main application file.\"\"\"

def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")
        
        (temp_path / "docs").mkdir()
        (temp_path / "docs" / "api.md").write_text("""
# API Documentation

## Functions

### hello_world()
Prints a greeting message.
""")
        
        # Create config for the server
        config_content = f"""
server:
  name: "ExampleDataSage"
  description: "Example DataSage server"
paths:
  - path: "{temp_dir}"
    description: "Test files"
settings:
  max_depth: 3
tools:
  search:
    description: "Search through test files"
    max_results: 10
"""
        
        config_path = temp_path / "config.yaml"
        config_path.write_text(config_content)
        
        # Create DataSage server
        print("Creating DataSage server...")
        server = create_server(str(config_path))
        
        # Connect to server using FastMCP client
        print("Connecting to server...")
        async with Client(server) as client:
            
            # List available tools
            print("\n=== Available Tools ===")
            tools = await client.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Test search tool
            print("\n=== Search Test ===")
            search_result = await client.call_tool("search", {
                "query": "hello",
                "search_type": "both",
                "match_type": "fuzzy"
            })
            print("Search results:")
            print(search_result.content[0].text)
            
            # Test get_page tool
            print("\n=== Get Page Test ===")
            page_result = await client.call_tool("get_page", {
                "path": str(temp_path / "readme.md")
            })
            print("File content:")
            print(page_result.content[0].text[:200] + "..." if len(page_result.content[0].text) > 200 else page_result.content[0].text)
            
            # Test get_page_children tool
            print("\n=== Directory Listing Test ===")
            children_result = await client.call_tool("get_page_children", {
                "path": str(temp_path),
                "max_depth": 2,
                "include_files": True,
                "include_dirs": True
            })
            print("Directory contents:")
            print(children_result.content[0].text)
            
        print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
