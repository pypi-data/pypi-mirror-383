"""
Database connection manager.
Handles SQLAlchemy connections, pooling, and query execution.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import re

from db_mcp.config import DatabaseConfig


class DatabaseManager:
    """Manages database connections and query execution."""
    
    def __init__(self, db_config: DatabaseConfig):
        self.config = db_config
        self.engine: Optional[Engine] = None
        self._connect()
    
    def _connect(self):
        """Create database engine with connection pooling."""
        connection_string = self.config.get_connection_string()
        
        try:
            self.engine = create_engine(
                connection_string,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_pre_ping=True,  # Test connections before use
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False  # Set to True for SQL debugging
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(f"Connected to database '{self.config.name}' ({self.config.type})")
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to database '{self.config.name}': {str(e)}"
            )
    
    def _is_read_query(self, query: str) -> bool:
        """Check if query is read-only (SELECT)."""
        # Remove comments and whitespace
        clean_query = re.sub(r'--.*?$', '', query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        clean_query = clean_query.strip().upper()
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TRUNCATE', 'REPLACE', 'MERGE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in clean_query:
                return False
        
        return clean_query.startswith('SELECT') or clean_query.startswith('WITH')
    
    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            limit: Maximum number of rows to return
        
        Returns:
            Dictionary with query results and metadata
        """
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        # Security check for read-only mode
        if self.config.read_only and not self._is_read_query(query):
            return {
                "success": False,
                "error": "Only SELECT queries are allowed in read-only mode"
            }
        
        try:
            with self.engine.connect() as conn:
                # Add LIMIT if it's a SELECT query and no LIMIT exists
                modified_query = query.strip()
                if modified_query.upper().startswith('SELECT') and 'LIMIT' not in modified_query.upper():
                    modified_query = f"{modified_query} LIMIT {limit}"
                
                result = conn.execute(text(modified_query))
                
                # If it's a SELECT query, fetch results
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    return {
                        "success": True,
                        "data": data,
                        "row_count": len(data),
                        "columns": list(columns)
                    }
                else:
                    # For INSERT/UPDATE/DELETE
                    conn.commit()
                    return {
                        "success": True,
                        "rows_affected": result.rowcount,
                        "message": f"Query executed successfully. Rows affected: {result.rowcount}"
                    }
                    
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": f"SQL Error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_schema(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            table_name: Optional specific table name
        
        Returns:
            Schema information as dictionary
        """
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        try:
            inspector = inspect(self.engine)
            
            if table_name:
                # Get specific table schema
                if table_name not in inspector.get_table_names():
                    return {
                        "success": False,
                        "error": f"Table '{table_name}' not found"
                    }
                
                columns = inspector.get_columns(table_name)
                
                return {
                    "success": True,
                    "table": table_name,
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col.get("nullable", True),
                            "default": col.get("default"),
                            "primary_key": col.get("primary_key", False)
                        }
                        for col in columns
                    ]
                }
            else:
                # Get all tables
                tables = inspector.get_table_names()
                
                schema_info = []
                for table in tables:
                    columns = inspector.get_columns(table)
                    schema_info.append({
                        "table": table,
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"])
                            }
                            for col in columns
                        ]
                    })
                
                return {
                    "success": True,
                    "database": self.config.name,
                    "table_count": len(tables),
                    "tables": schema_info
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting schema: {str(e)}"
            }
    
    def explain_query(self, query: str) -> Dict[str, Any]:
        """
        Get query execution plan.
        
        Args:
            query: SQL query to explain
        
        Returns:
            Query execution plan
        """
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        try:
            with self.engine.connect() as conn:
                # Different databases use different EXPLAIN syntax
                if self.config.type == "postgresql":
                    explain_query = f"EXPLAIN (FORMAT JSON) {query}"
                elif self.config.type == "mysql":
                    explain_query = f"EXPLAIN {query}"
                elif self.config.type == "sqlite":
                    explain_query = f"EXPLAIN QUERY PLAN {query}"
                else:
                    explain_query = f"EXPLAIN {query}"
                
                result = conn.execute(text(explain_query))
                rows = result.fetchall()
                columns = result.keys()
                
                plan = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "success": True,
                    "query": query,
                    "execution_plan": plan
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error explaining query: {str(e)}"
            }
    
    def get_table_sample(self, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get sample rows from a table.
        
        Args:
            table_name: Table name
            limit: Number of rows to fetch
        
        Returns:
            Sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query, limit=limit)
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            print(f"Closed connection to '{self.config.name}'")


class DatabasePool:
    """Manages multiple database connections."""
    
    def __init__(self):
        self.databases: Dict[str, DatabaseManager] = {}
    
    def add_database(self, db_config: DatabaseConfig):
        """Add a database to the pool."""
        manager = DatabaseManager(db_config)
        self.databases[db_config.name] = manager
    
    def get_database(self, name: str) -> Optional[DatabaseManager]:
        """Get a database manager by name."""
        return self.databases.get(name)
    
    def list_databases(self) -> List[str]:
        """List all available database names."""
        return list(self.databases.keys())
    
    def close_all(self):
        """Close all database connections."""
        for db in self.databases.values():
            db.close()