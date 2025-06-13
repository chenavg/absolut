import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', ''),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'absolut_banking'),
    'ssl_ca': 'rds-ca-2019-root.pem',
    'ssl_verify_cert': True
} 