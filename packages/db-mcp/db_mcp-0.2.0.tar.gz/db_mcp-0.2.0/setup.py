"""
Setup configuration for db-mcp package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="db-mcp",
    version="0.2.0",
    author="DB-MCP Contributors",
    author_email="fenilramoliya2103@gmail.com",
    description="Universal MCP server for connecting Claude to SQL databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fenil210/Database-MCP",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mysql": ["mysql-connector-python>=8.0.0"],
        "mssql": ["pyodbc>=4.0.0"],
        "all": [
            "psycopg2-binary>=2.9.0",
            "mysql-connector-python>=8.0.0",
            "pyodbc>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "db-mcp=db_mcp.server:main",
        ],
    },
    keywords=["mcp", "database", "sql", "claude", "ai", "postgresql", "mysql", "sqlite", "sqlserver"],
    project_urls={
        "Bug Reports": "https://github.com/fenil210/Database-MCP/issues",
        "Source": "https://github.com/fenil210/Database-MCP",
        "Documentation": "https://github.com/fenil210/Database-MCP/blob/main/README.md",
    },
)