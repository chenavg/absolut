import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        # Print connection details (without password) for debugging
        print(f"Attempting to connect to database:")
        print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"Port: {os.getenv('DB_PORT', '3306')}")
        print(f"Database: {os.getenv('DB_NAME', 'openbanking')}")
        print(f"User: {os.getenv('DB_USER', 'root')}")
        
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            database=os.getenv('DB_NAME', 'openbanking'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            cursor.close()
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}", file=sys.stderr)
        print(f"Error Code: {e.errno}", file=sys.stderr)
        print(f"SQLSTATE: {e.sqlstate}", file=sys.stderr)
        print(f"Error Message: {e.msg}", file=sys.stderr)
        return None

def init_db():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id VARCHAR(36) PRIMARY KEY,
                    account_type VARCHAR(20) NOT NULL,
                    balance DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    created_at DATETIME NOT NULL
                )
            """)
            
            connection.commit()
            print("Database tables initialized successfully")
        except Error as e:
            print(f"Error initializing database: {e}", file=sys.stderr)
            print(f"Error Code: {e.errno}", file=sys.stderr)
            print(f"SQLSTATE: {e.sqlstate}", file=sys.stderr)
            print(f"Error Message: {e.msg}", file=sys.stderr)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("Database connection closed") 