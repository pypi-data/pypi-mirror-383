"""
Configuration management for DB-MCP server.
Handles loading and validating database connection configurations.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Represents a single database configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.type = config.get("type", "").lower()
        self.host = config.get("host")
        self.port = config.get("port")
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")
        self.path = config.get("path")  # For SQLite
        self.read_only = config.get("read_only", True)
        self.pool_size = config.get("pool_size", 5)
        self.max_overflow = config.get("max_overflow", 2)
        self.pool_timeout = config.get("pool_timeout", 30)
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate the database configuration."""
        if not self.type:
            raise ValueError(f"Database '{self.name}': 'type' is required")
        
        supported_types = ["postgresql", "mysql", "sqlite", "mssql"]
        if self.type not in supported_types:
            raise ValueError(
                f"Database '{self.name}': Unsupported type '{self.type}'. "
                f"Supported: {', '.join(supported_types)}"
            )
        
        # SQLite only needs path
        if self.type == "sqlite":
            if not self.path:
                raise ValueError(f"Database '{self.name}': SQLite requires 'path'")
        else:
            # Other databases need host and database name
            if not self.host:
                raise ValueError(f"Database '{self.name}': 'host' is required")
            if not self.database:
                raise ValueError(f"Database '{self.name}': 'database' is required")
    
    def get_connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        if self.type == "sqlite":
            # Convert to absolute path
            path = Path(self.path).resolve()
            return f"sqlite:///{path}"
        
        # For other databases
        password = self.password or ""
        username = self.username or ""
        
        # Check for environment variable references
        if password.startswith("$"):
            password = os.getenv(password[1:], "")
        if username.startswith("$"):
            username = os.getenv(username[1:], "")
        
        # Build connection string
        auth = f"{username}:{password}@" if username else ""
        port_str = f":{self.port}" if self.port else ""
        
        if self.type == "postgresql":
            return f"postgresql://{auth}{self.host}{port_str}/{self.database}"
        elif self.type == "mysql":
            return f"mysql+mysqlconnector://{auth}{self.host}{port_str}/{self.database}"
        elif self.type == "mssql":
            # For SQL Server, we need to specify the driver
            driver = "ODBC+Driver+17+for+SQL+Server"
            return f"mssql+pyodbc://{auth}{self.host}{port_str}/{self.database}?driver={driver}"
        
        raise ValueError(f"Unknown database type: {self.type}")


class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.databases: Dict[str, DatabaseConfig] = {}
        
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str):
        """Load configuration from JSON file."""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Load database configurations
        databases_config = data.get("databases", {})
        
        if not databases_config:
            raise ValueError("No databases defined in configuration")
        
        for name, db_config in databases_config.items():
            self.databases[name] = DatabaseConfig(name, db_config)
        
        print(f"Loaded {len(self.databases)} database(s): {', '.join(self.databases.keys())}")
    
    def get_database(self, name: str) -> Optional[DatabaseConfig]:
        """Get a specific database configuration."""
        return self.databases.get(name)
    
    def list_databases(self) -> list[str]:
        """List all configured database names."""
        return list(self.databases.keys())