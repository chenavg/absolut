import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, List, Optional, Tuple

class GenericDAO:
    def __init__(self, db_config: Dict[str, Any]):
        """Initialize the DAO with database configuration."""
        self.db_config = db_config
        self.connection = None
        self.connect()
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
        except Error as e:
            raise Exception(f"Error connecting to MySQL database: {str(e)}")
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def create(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Create a new record in the specified table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of field-value pairs
            
        Returns:
            int: ID of the created record
        """
        try:
            cursor = self.connection.cursor()
            
            # Build the INSERT query
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
            
            # Execute the query
            cursor.execute(query, list(data.values()))
            self.connection.commit()
            
            # Get the ID of the created record
            record_id = cursor.lastrowid
            
            cursor.close()
            return record_id
            
        except Error as e:
            self.connection.rollback()
            raise Exception(f"Error creating record: {str(e)}")
    
    def read(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Read records from the specified table.
        
        Args:
            table_name: Name of the table
            conditions: Optional dictionary of field-value pairs for WHERE clause
            
        Returns:
            List of dictionaries containing the records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Build the SELECT query
            query = f"SELECT * FROM {table_name}"
            params = []
            
            if conditions:
                where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                query += f" WHERE {where_clause}"
                params.extend(conditions.values())
            
            # Execute the query
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            return results
            
        except Error as e:
            raise Exception(f"Error reading records: {str(e)}")
    
    def update(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        """
        Update records in the specified table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of field-value pairs to update
            conditions: Dictionary of field-value pairs for WHERE clause
            
        Returns:
            int: Number of affected rows
        """
        try:
            cursor = self.connection.cursor()
            
            # Build the UPDATE query
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            
            # Combine parameters
            params = list(data.values()) + list(conditions.values())
            
            # Execute the query
            cursor.execute(query, params)
            self.connection.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
            
        except Error as e:
            self.connection.rollback()
            raise Exception(f"Error updating records: {str(e)}")
    
    def delete(self, table_name: str, conditions: Dict[str, Any]) -> int:
        """
        Delete records from the specified table.
        
        Args:
            table_name: Name of the table
            conditions: Dictionary of field-value pairs for WHERE clause
            
        Returns:
            int: Number of affected rows
        """
        try:
            cursor = self.connection.cursor()
            
            # Build the DELETE query
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            # Execute the query
            cursor.execute(query, list(conditions.values()))
            self.connection.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
            
        except Error as e:
            self.connection.rollback()
            raise Exception(f"Error deleting records: {str(e)}") 