import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'absolut.cluster-cfam0y0sea88.us-west-2.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123'),
    'database': os.getenv('DB_NAME', 'absolut_banking'),
    'ssl_ca': 'rds-ca-2019-root.pem',
    'ssl_verify_cert': True
} 