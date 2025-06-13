import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                # Verify SSL certificate exists
                if not os.path.exists(DB_CONFIG['ssl_ca']):
                    raise FileNotFoundError(f"SSL CA certificate not found at {DB_CONFIG['ssl_ca']}")
                
                # Create connection with SSL
                self.connection = mysql.connector.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    database=DB_CONFIG['database'],
                    ssl_ca=DB_CONFIG['ssl_ca'],
                    ssl_verify_cert=DB_CONFIG['ssl_verify_cert']
                )
                logger.info("Successfully connected to MySQL database with SSL")
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            raise

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            self.disconnect()

    def execute_update(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()

    def initialize_tables(self):
        """Initialize database tables if they don't exist"""
        create_tables_queries = [
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR(36) PRIMARY KEY,
                account_type VARCHAR(20) NOT NULL,
                balance DECIMAL(15,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS beneficiaries (
                beneficiary_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                account_number VARCHAR(50) NOT NULL,
                bank_code VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id VARCHAR(36) PRIMARY KEY,
                amount DECIMAL(15,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                beneficiary_id VARCHAR(36) NOT NULL,
                status VARCHAR(20) NOT NULL,
                type VARCHAR(20) NOT NULL,
                scheduled_date TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
            )
            """
        ]

        try:
            self.connect()
            cursor = self.connection.cursor()
            for query in create_tables_queries:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            logger.info("Database tables initialized successfully")
        except Error as e:
            logger.error(f"Error initializing tables: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()

# Create a singleton instance
db = Database() 