"""
DB-MCP: Database Model Context Protocol Server
A universal MCP server for connecting Claude to any SQL database.
"""

__version__ = "0.1.0"
__author__ = "DB-MCP Contributors"

from db_mcp.server import main

__all__ = ["main"]