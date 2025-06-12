import json
import logging
import traceback
from decimal import Decimal
from datetime import datetime, date

# Configure logging first
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import local modules after logging setup
from dao import DatabaseDAO
from db_config import DB_CONFIG

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(make_json_serializable(i) for i in obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def validate_table_name(table_name):
    """Validate table name to prevent SQL injection."""
    if not table_name or not isinstance(table_name, str):
        return False
    # Only allow alphanumeric characters and underscores
    return all(c.isalnum() or c == '_' for c in table_name)

def lambda_handler(event, context):
    """Lambda function handler for database operations."""
    logger.info(f"Received event: {event}")
    logger.info(f"Event type: {type(event)}")
    
    # Handle string event (from API Gateway) or HTTP API Gateway event with 'body'
    if isinstance(event, str):
        try:
            event = json.loads(event)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON format'})
            }
    elif isinstance(event, dict) and 'body' in event:
        try:
            body = event['body']
            if isinstance(body, str):
                event = json.loads(body)
            else:
                event = body
        except Exception as e:
            logger.error(f"Error decoding event body: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid body format'})
            }
    
    try:
        # Initialize DAO
        dao = DatabaseDAO(DB_CONFIG)
        
        # Get action from event
        action = event.get('action', '').lower()
        logger.info(f"Received action: '{action}'")
        logger.info(f"Raw event: {json.dumps(event)}")
        
        # Handle list_tables action
        if action == 'list_tables':
            try:
                logger.info("Starting list_tables operation")
                logger.info(f"Database configuration: {DB_CONFIG['database']}")
                
                # Verify connection
                if not dao.connection or not dao.connection.is_connected():
                    error_msg = "Database connection is not active"
                    logger.error(error_msg)
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            'error': error_msg,
                            'details': 'Failed to establish database connection'
                        })
                    }
                
                # Query to get all tables in the database
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
                """
                logger.info(f"Executing query: {query} with params: {DB_CONFIG['database']}")
                tables = dao.execute_query(query, (DB_CONFIG['database'],))
                logger.info(f"Query executed successfully. Found {len(tables)} tables")
                
                table_list = [table[0] for table in tables]
                logger.info(f"Tables found: {table_list}")
                
                serializable_result = make_json_serializable({
                    'tables': table_list,
                    'database': DB_CONFIG['database']
                })
                return {
                    'statusCode': 200,
                    'body': json.dumps(serializable_result)
                }
            except Exception as e:
                error_msg = f"Error listing tables: {str(e)}"
                logger.error(error_msg)
                # Get the full exception details
                error_details = traceback.format_exc()
                logger.error(f"Full error details: {error_details}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'error': error_msg,
                        'details': error_details,
                        'type': type(e).__name__
                    })
                }
        
        # Only validate table_name for actions that require it
        if action in ['read', 'create', 'update', 'delete']:
            table_name = event.get('table_name')
            if not validate_table_name(table_name):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid table name'})
                }
        else:
            table_name = None
        
        # Handle other actions
        if action == 'read':
            conditions = event.get('conditions', {})
            result = dao.read(table_name, conditions)
            serializable_result = make_json_serializable(result)
            return {
                'statusCode': 200,
                'body': json.dumps(serializable_result)
            }
        elif action == 'create':
            data = event.get('data', {})
            if not data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No data provided for create operation'})
                }
            result = dao.create(table_name, data)
            serializable_result = make_json_serializable(result)
            return {
                'statusCode': 201,
                'body': json.dumps(serializable_result)
            }
        elif action == 'update':
            data = event.get('data', {})
            conditions = event.get('conditions', {})
            if not data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No data provided for update operation'})
                }
            result = dao.update(table_name, data, conditions)
            serializable_result = make_json_serializable(result)
            return {
                'statusCode': 200,
                'body': json.dumps(serializable_result)
            }
        elif action == 'delete':
            conditions = event.get('conditions', {})
            result = dao.delete(table_name, conditions)
            serializable_result = make_json_serializable(result)
            return {
                'statusCode': 200,
                'body': json.dumps(serializable_result)
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid action',
                    'supported_actions': ['read', 'create', 'update', 'delete', 'list_tables']
                })
            }
            
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        # Get the full exception details
        error_details = traceback.format_exc()
        logger.error(f"Full error details: {error_details}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'details': error_details,
                'type': type(e).__name__
            })
        }
    finally:
        if 'dao' in locals():
            dao.close() 