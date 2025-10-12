"""
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Database integration module for PowerScript
Provides simple database operations using SQLite
"""

import sqlite3
from typing import List, Dict, Any, Optional


class Database:
    """Simple database wrapper for SQLite"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> None:
        """Connect to the database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self) -> None:
        """Disconnect from the database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query"""
        if not self.connection:
            self.connect()
        return self.connection.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row as dict"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dicts"""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def commit(self) -> None:
        """Commit changes"""
        if self.connection:
            self.connection.commit()
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """Create a table with given columns"""
        cols = ", ".join(f"{name} {type_}" for name, type_ in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})"
        self.execute(query)
        self.commit()
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert data into table, return rowid"""
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        cursor = self.execute(query, values)
        self.commit()
        return cursor.lastrowid
    
    def select(self, table_name: str, where: Optional[Dict[str, Any]] = None, 
               columns: List[str] = None) -> List[Dict[str, Any]]:
        """Select from table"""
        cols = "*" if columns is None else ", ".join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        params = ()
        if where:
            conditions = " AND ".join(f"{k} = ?" for k in where.keys())
            query += f" WHERE {conditions}"
            params = tuple(where.values())
        return self.fetch_all(query, params)


# Convenience functions
def create_database(db_path: str = ":memory:") -> Database:
    """Create a new database instance"""
    return Database(db_path)