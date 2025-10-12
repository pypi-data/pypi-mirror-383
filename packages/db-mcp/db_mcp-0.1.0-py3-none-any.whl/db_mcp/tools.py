"""
MCP Tool definitions for database operations.
Defines the tools that Claude can use to interact with databases.
"""

from typing import Any, Dict
from mcp.types import Tool


# Tool definitions
def get_tool_definitions() -> list[Tool]:
    """Return list of all available MCP tools."""
    
    return [
        Tool(
            name="list_databases",
            description="List all available databases configured in the server. Returns the names of all databases that can be queried.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="get_schema",
            description="Get the schema information for a database. If table_name is provided, returns detailed schema for that specific table. Otherwise, returns a list of all tables with their columns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Optional: specific table name to get detailed schema"
                    }
                },
                "required": ["database"]
            }
        ),
        
        Tool(
            name="execute_query",
            description="Execute a SQL query on the specified database. For read-only databases, only SELECT queries are allowed. Results are limited to 100 rows by default. Use this for complex queries, aggregations, joins, and filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database to query"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (must be SELECT for read-only databases)"
                    }
                },
                "required": ["database", "query"]
            }
        ),
        
        Tool(
            name="explain_query",
            description="Get the execution plan for a SQL query without actually running it. Useful for understanding how the database will execute a query and for optimization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to explain"
                    }
                },
                "required": ["database", "query"]
            }
        ),
        
        Tool(
            name="get_table_sample",
            description="Get a quick sample of rows from a specific table. Returns the first 10 rows by default. Useful for quickly inspecting table contents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Name of the database"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to sample"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of rows to return (default: 10, max: 100)",
                        "default": 10
                    }
                },
                "required": ["database", "table_name"]
            }
        )
    ]


def format_result_for_claude(result: Dict[str, Any]) -> str:
    """
    Format database query results in a readable way for Claude.
    
    Args:
        result: Result dictionary from database operations
    
    Returns:
        Formatted string representation
    """
    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error')}"
    
    # Handle different result types
    if "data" in result:
        # Query results with data
        data = result["data"]
        row_count = result.get("row_count", 0)
        
        if row_count == 0:
            return "Query executed successfully. No rows returned."
        
        # Format as a readable table-like structure
        import json
        formatted = json.dumps(data, indent=2, default=str)
        
        return f"Query returned {row_count} row(s):\n\n{formatted}"
    
    elif "tables" in result:
        # Schema information
        tables = result["tables"]
        table_count = result.get("table_count", 0)
        
        output = [f"Database contains {table_count} table(s):\n"]
        
        for table_info in tables:
            table_name = table_info["table"]
            columns = table_info["columns"]
            output.append(f"\nTable: {table_name}")
            output.append("Columns:")
            for col in columns:
                output.append(f"  - {col['name']} ({col['type']})")
        
        return "\n".join(output)
    
    elif "table" in result and "columns" in result:
        # Single table schema
        table_name = result["table"]
        columns = result["columns"]
        
        output = [f"Schema for table '{table_name}':\n"]
        
        for col in columns:
            nullable = "NULL" if col.get("nullable") else "NOT NULL"
            pk = " [PRIMARY KEY]" if col.get("primary_key") else ""
            output.append(f"  - {col['name']} {col['type']} {nullable}{pk}")
        
        return "\n".join(output)
    
    elif "execution_plan" in result:
        # Query execution plan
        import json
        plan = json.dumps(result["execution_plan"], indent=2, default=str)
        return f"Query Execution Plan:\n\n{plan}"
    
    elif "message" in result:
        # Generic success message
        return f"{result['message']}"
    
    elif "databases" in result:
        # List of databases
        databases = result["databases"]
        output = [f"Available databases ({len(databases)}):\n"]
        for db in databases:
            output.append(f"  - {db}")
        return "\n".join(output)
    
    else:
        # Fallback
        import json
        return json.dumps(result, indent=2, default=str)