from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
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
            cls._instance.engine = None
            cls._instance.Session = None
        return cls._instance

    def initialize(self):
        try:
            if self.engine is None:
                # Verify SSL certificate exists
                if not os.path.exists(DB_CONFIG['ssl_ca']):
                    raise FileNotFoundError(f"SSL CA certificate not found at {DB_CONFIG['ssl_ca']}")
                
                # Create database URL
                db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
                
                # Create engine with SSL configuration
                self.engine = create_engine(
                    db_url,
                    connect_args={
                        'ssl_ca': DB_CONFIG['ssl_ca'],
                        'ssl_verify_cert': DB_CONFIG['ssl_verify_cert']
                    }
                )
                
                # Create session factory
                session_factory = sessionmaker(bind=self.engine)
                self.Session = scoped_session(session_factory)
                
                logger.info("Successfully initialized SQLAlchemy engine and session")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self):
        if self.Session is None:
            self.initialize()
        return self.Session()

    def close_session(self, session):
        if session:
            session.close()

    def initialize_tables(self):
        """Initialize database tables if they don't exist"""
        try:
            from models import Base
            if self.engine is None:
                self.initialize()
            Base.metadata.create_all(self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
            raise

# Create a singleton instance
db = Database() 