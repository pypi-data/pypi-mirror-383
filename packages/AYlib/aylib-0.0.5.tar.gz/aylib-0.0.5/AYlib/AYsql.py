# -*- coding: utf-8 -*-
"""
AYsql - MySQL database operation module for AYlib
Usage: 
    1. Instantiate the AYDatabase class
    2. Use methods: db = AYDatabase() then db.fetch_all("sql")
"""
__doc__ = 'AYlib SQL module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import logging
from typing import Optional, Dict, List, Any, Union
from contextlib import contextmanager

try:
    import PyMySQL as MySQLdb
    PyMySQL.install_as_MySQLdb()
    import PyMySQL.cursors as cursors
    MYSQL_AVAILABLE = True
except ImportError:
    try:
        import MySQLdb
        import MySQLdb.cursors as cursors
        MYSQL_AVAILABLE = True
    except ImportError:
        MYSQL_AVAILABLE = False
        # Create dummy classes for when MySQL is not available
        class DummyMySQLdb:
            def connect(*args, **kwargs):
                raise ImportError("MySQLdb not available. Install with: pip install PyMySQL")
        MySQLdb = DummyMySQLdb()
        cursors = None

# Default configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'test',
    'charset': 'utf8mb4',
    'autocommit': True
}

class AYDatabase:
    """MySQL database operation class with improved error handling and resource management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize database connection.
        
        Args:
            config: Database configuration dictionary
            logger: Custom logger instance
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.logger = logger or self._setup_logger()
        self._conn = None
        self._cursor = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger for database operations."""
        logger = logging.getLogger('AYDatabase')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not MYSQL_AVAILABLE:
            self.logger.error("MySQL driver not available. Install with: pip install PyMySQL")
            return False
            
        try:
            self._conn = MySQLdb.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                passwd=self.config['password'],
                db=self.config['database'],
                charset=self.config['charset'],
                cursorclass=cursors.DictCursor,
                autocommit=self.config['autocommit']
            )
            self._cursor = self._conn.cursor()
            self.logger.info("Database connection established successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper cleanup of resources.
        """
        if not self._conn:
            if not self.connect():
                raise ConnectionError("Failed to establish database connection")
        
        try:
            yield self._conn, self._cursor
        except Exception as e:
            if self._conn:
                self._conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            # Connection cleanup is handled by close() method
            pass
    
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> Union[List[Dict], bool]:
        """
        Execute SELECT query and return all results.
        
        Args:
            sql: SQL query string
            params: Query parameters for prepared statement
            
        Returns:
            List of dictionaries or False on error
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or ())
                result = cursor.fetchall()
                self.logger.debug(f"Query executed successfully: {sql}")
                return list(result) if result else []
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return False
    
    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Union[Dict, bool]:
        """
        Execute SELECT query and return one result.
        
        Args:
            sql: SQL query string
            params: Query parameters for prepared statement
            
        Returns:
            Dictionary or False on error
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or ())
                result = cursor.fetchone()
                self.logger.debug(f"Query executed successfully: {sql}")
                return dict(result) if result else {}
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return False
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> bool:
        """
        Execute INSERT, UPDATE, DELETE queries.
        
        Args:
            sql: SQL query string
            params: Query parameters for prepared statement
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or ())
                if not self.config['autocommit']:
                    conn.commit()
                self.logger.debug(f"Query executed successfully: {sql}")
                return True
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return False
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> bool:
        """
        Execute multiple queries with different parameters.
        
        Args:
            sql: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.executemany(sql, params_list)
                if not self.config['autocommit']:
                    conn.commit()
                self.logger.debug(f"Batch query executed successfully: {sql}")
                return True
        except Exception as e:
            self.logger.error(f"Batch query execution failed: {e}")
            return False
    
    def get_last_insert_id(self) -> int:
        """
        Get the last inserted row ID.
        
        Returns:
            int: Last insert ID or 0 on error
        """
        try:
            if self._cursor:
                return self._cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to get last insert ID: {e}")
        return 0
    
    def close(self) -> None:
        """Close database connection and cursor."""
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            if self._conn:
                self._conn.close()
                self._conn = None
            self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.warning(f"Error closing database connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure connection cleanup."""
        self.close()

# Backward compatibility alias
database = AYDatabase

# Example usage
if __name__ == '__main__':
    # Example configuration
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'your_password',
        'database': 'test_db'
    }
    
    # Using context manager (recommended)
    try:
        with AYDatabase(config) as db:
            # Create table example
            create_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE
            )
            """
            db.execute(create_sql)
            
            # Insert data example
            insert_sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
            db.execute(insert_sql, ('John Doe', 'john@example.com'))
            
            # Query data example
            users = db.fetch_all("SELECT * FROM users")
            print("Users:", users)
            
    except Exception as e:
        print(f"Database operation failed: {e}")