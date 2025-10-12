"""
Main MCP Server for database operations.
Handles MCP protocol communication and routes tool calls to database operations.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

from db_mcp.config import Config
from db_mcp.database import DatabasePool
from db_mcp.tools import get_tool_definitions, format_result_for_claude


class DBMCPServer:
    """Database MCP Server implementation."""
    
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self.db_pool = DatabasePool()
        self.app = Server("db-mcp")
        
        # Initialize all databases
        for db_name, db_config in self.config.databases.items():
            try:
                self.db_pool.add_database(db_config)
            except Exception as e:
                print(f"Warning: Failed to connect to '{db_name}': {e}")
        
        # Setup MCP handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Register all MCP protocol handlers."""
        
        @self.app.list_tools()
        async def list_tools():
            """Return available tools."""
            return get_tool_definitions()
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool execution requests."""
            try:
                result = await self._execute_tool(name, arguments)
                formatted = format_result_for_claude(result)
                
                return [TextContent(
                    type="text",
                    text=formatted
                )]
                
            except Exception as e:
                error_msg = f"Error executing tool '{name}': {str(e)}"
                print(f"ERROR: {error_msg}")
                return [TextContent(
                    type="text",
                    text=f"ERROR: {error_msg}"
                )]
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Execute a specific tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
        
        Returns:
            Result dictionary
        """
        if tool_name == "list_databases":
            return {
                "success": True,
                "databases": self.db_pool.list_databases()
            }
        
        # All other tools require a database parameter
        database_name = arguments.get("database")
        if not database_name:
            return {
                "success": False,
                "error": "Missing required parameter: database"
            }
        
        db = self.db_pool.get_database(database_name)
        if not db:
            return {
                "success": False,
                "error": f"Database '{database_name}' not found. Available: {', '.join(self.db_pool.list_databases())}"
            }
        
        # Route to appropriate handler
        if tool_name == "get_schema":
            table_name = arguments.get("table_name")
            return db.get_schema(table_name)
        
        elif tool_name == "execute_query":
            query = arguments.get("query")
            if not query:
                return {
                    "success": False,
                    "error": "Missing required parameter: query"
                }
            return db.execute_query(query)
        
        elif tool_name == "explain_query":
            query = arguments.get("query")
            if not query:
                return {
                    "success": False,
                    "error": "Missing required parameter: query"
                }
            return db.explain_query(query)
        
        elif tool_name == "get_table_sample":
            table_name = arguments.get("table_name")
            if not table_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: table_name"
                }
            limit = arguments.get("limit", 10)
            return db.get_table_sample(table_name, limit)
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    async def run(self):
        """Run the MCP server."""
        print("\n" + "="*50)
        print("DB-MCP Server Starting...")
        print("="*50)
        
        async with stdio_server() as (read_stream, write_stream):
            print("Server ready and listening for connections")
            print("="*50 + "\n")
            
            try:
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )
            finally:
                # Cleanup
                self.db_pool.close_all()
                print("\nServer shutdown complete")


def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description="DB-MCP: Database Model Context Protocol Server"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to configuration JSON file"
    )
    
    args = parser.parse_args()
    
    try:
        server = DBMCPServer(args.config)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n\nServer interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()