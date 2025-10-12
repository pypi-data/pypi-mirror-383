"""
Main MCP Server for database operations.
Handles MCP protocol communication and routes tool calls to database operations.
"""

import asyncio
import argparse
import sys
import json
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


def generate_example_config():
    """Generate an example config.json file."""
    example_config = {
        "databases": {
            "my_postgres_db": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "mydb",
                "username": "user",
                "password": "password",
                "read_only": True,
                "pool_size": 5,
                "max_overflow": 2
            },
            "my_mysql_db": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "database": "mydb",
                "username": "root",
                "password": "root",
                "read_only": True,
                "pool_size": 5
            },
            "my_sqlite_db": {
                "type": "sqlite",
                "path": "./database.db",
                "read_only": False
            }
        }
    }
    
    config_path = Path("config.json")
    
    if config_path.exists():
        print(f"Error: config.json already exists!")
        print(f"Please delete it first or use a different name.")
        return 1
    
    with open(config_path, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print("\n" + "="*60)
    print("SUCCESS: config.json created!")
    print("="*60)
    print("\nGenerated example configuration file with 3 databases:")
    print("  - my_postgres_db (PostgreSQL)")
    print("  - my_mysql_db (MySQL)")
    print("  - my_sqlite_db (SQLite)")
    print("\nNext steps:")
    print("1. Edit config.json with your actual database details")
    print("2. Remove database entries you don't need")
    print("3. Install required database drivers:")
    print("   - PostgreSQL: pip install psycopg2-binary")
    print("   - MySQL: pip install mysql-connector-python")
    print("   - SQL Server: pip install pyodbc")
    print("4. Run: db-mcp --config config.json")
    print("\nFor environment variables (recommended for passwords):")
    print("  - Use $VAR_NAME in config.json")
    print("  - Set in .env file or system environment")
    print("="*60 + "\n")
    
    return 0


def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description="DB-MCP: Database Model Context Protocol Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate example config file
  db-mcp --init
  
  # Run server with config file
  db-mcp --config config.json
  
  # Run with custom config location
  db-mcp --config /path/to/my-config.json

For more information, visit: https://github.com/fenil210/Database-MCP
        """
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Generate example config.json file"
    )
    
    args = parser.parse_args()
    
    # Handle --init command
    if args.init:
        sys.exit(generate_example_config())
    
    # Require --config if not --init
    if not args.config:
        parser.error("--config is required (or use --init to generate example config)")
    
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