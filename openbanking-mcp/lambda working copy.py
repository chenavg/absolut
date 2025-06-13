from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, get_origin, get_args
from enum import Enum
import json
import logging
import uuid
from datetime import datetime, timedelta
import mysql.connector
from database import db
#import requests  # Add this import at the top with other imports

db.initialize_tables()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define request/response models
class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

class Account(BaseModel):
    """Base model representing an account in the database"""
    account_id: Optional[str] = Field(None, description="Unique account identifier (UUID). If not provided, a new UUID will be generated")
    type: AccountType = Field(..., description="Type of account")
    balance: float = Field(default=0.0, description="Current account balance")  # Set default to 0.0
    currency: str = Field(..., description="Account currency code (3 letters)", pattern="^[A-Z]{3}$")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")

class AccountRequest(Account):
    """Model for account creation requests"""
    account_id: Optional[str] = Field(None, description="Unique account identifier (UUID). If not provided, a new UUID will be generated")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Account creation timestamp")
    balance: float = Field(default=0.0, description="Current account balance")  # Set default to 0.0

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

class PaymentType(str, Enum):
    TRANSFER = "transfer"
    BILL_PAYMENT = "bill_payment"
    WIRE_TRANSFER = "wire_transfer"
    ACH = "ach"
    CARD_PAYMENT = "card_payment"

class Payment(BaseModel):
    """Base model representing a payment in the database"""
    payment_id: str = Field(..., description="Unique payment identifier (UUID)")
    amount: float = Field(..., description="Payment amount", gt=0)
    currency: str = Field(..., description="Payment currency code (3 letters)", pattern="^[A-Z]{3}$")
    beneficiary_id: str = Field(..., description="ID of the beneficiary receiving the payment")
    source_account_id: str = Field(..., description="ID of the source account")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Current status of the payment")
    type: PaymentType = Field(..., description="Type of payment")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date for the payment (if applicable)")
    created_at: datetime = Field(default_factory=datetime.now, description="Payment creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when the payment was completed")

class PaymentRequest(Payment):
    """Model for payment creation requests"""
    payment_id: Optional[str] = Field(None, description="Unique payment identifier (UUID). If not provided, a new UUID will be generated")
    source_account_id: str = Field(..., description="ID of the source account")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Payment creation timestamp")

class PaymentResponse(Payment):
    """Model for payment responses"""
    pass

class Beneficiary(BaseModel):
    """Base model representing a beneficiary in the database"""
    beneficiary_id: str = Field(..., description="Unique beneficiary identifier (UUID)")
    name: str = Field(..., description="Beneficiary name", min_length=1, max_length=100)
    account_number: str = Field(..., description="Beneficiary's account number", min_length=1, max_length=50)
    bank_code: str = Field(..., description="Bank code/identifier", min_length=1, max_length=20)
    created_at: datetime = Field(default_factory=datetime.now, description="Beneficiary creation timestamp")

class BeneficiaryRequest(Beneficiary):
    """Model for beneficiary creation requests"""
    beneficiary_id: Optional[str] = Field(None, description="Unique beneficiary identifier (UUID). If not provided, a new UUID will be generated")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Beneficiary creation timestamp")

class BeneficiaryResponse(Beneficiary):
    """Model for beneficiary responses"""
    pass

# Tool decorator for documentation
def banking_tool(description: str, request_model: BaseModel = None, response_model: BaseModel = None):
    def decorator(func):
        func._tool_description = description
        func._request_model = request_model
        func._response_model = response_model
        func._tool_name = func.__name__
        return func
    return decorator

# Banking tool implementations
@banking_tool(
    description="List all accounts for a customer",
    response_model=List[Account]
)
def list_accounts(customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all accounts, optionally filtered by customer"""
    try:
        # Fetch accounts from database
        query = "SELECT * FROM accounts"
        params = []
        if customer_id:
            query += " WHERE customer_id = %s"
            params.append(customer_id)
            
        accounts_data = db.execute_query(query, params)
        
        # Transform database results to match the expected structure
        accounts = []
        for acc in accounts_data:
            accounts.append({
                "id": acc["account_id"],
                "name": f"{acc['account_type'].title()} Account",  # Generate a name based on account type
                "type": AccountType(acc["account_type"].lower()),
                "balance": float(acc["balance"]),
                "currency": acc["currency"]
            })
            
        return accounts
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise

@banking_tool(
    description="Create a new bank account",
    request_model=AccountRequest,
    response_model=Account
)
def create_account(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new bank account with validation and database insertion"""
    try:
        # Validate and prepare request
        request = AccountRequest(**request_data)
        account_id = request.account_id if request.account_id else str(uuid.uuid4())
        logger.info(f"Creating new account with ID: {account_id}")
        
        # Create account object
        new_account = Account(
            account_id=account_id,
            type=request.type,
            balance=request.balance,
            currency=request.currency,
            created_at=request.created_at
        )
        
        # Prepare insert query
        insert_account_query = """
            INSERT INTO accounts 
            (account_id, account_type, balance, currency, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Prepare parameters
        insert_params = [
            new_account.account_id,
            new_account.type.value,  # Convert enum to string
            new_account.balance,
            new_account.currency,
            new_account.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        # Prepare transaction query
        transaction_queries = [
            {
                'query': insert_account_query,
                'params': insert_params,
                'type': 'INSERT'
            }
        ]
        
        # Execute transaction
        try:
            logger.info("Executing account creation transaction...")
            result = db.execute_transaction(transaction_queries)
            
            if result['transaction_success']:
                logger.info("Account created successfully")
                logger.info(f"Account inserted with ID: {result['lastrowid']}")
                
                # Verify the insert affected one row
                insert_result = result['results'][0]
                if insert_result['affected_rows'] != 1:
                    logger.warning(f"Expected 1 account to be inserted, but got {insert_result['affected_rows']}")
                
                return new_account.model_dump(mode='json')
            else:
                raise ValueError("Account creation failed to complete successfully")
                
        except ValueError as e:
            logger.error(f"Account creation transaction failed: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error in create_account: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid request data: {str(e)}")

@banking_tool(
    description="List all payments",
    response_model=List[Payment]
)
def list_payments(beneficiary_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all payments, optionally filtered by beneficiary"""
    try:
        # Fetch payments from database
        query = "SELECT * FROM payments"
        params = []
        if beneficiary_id:
            query += " WHERE beneficiary_id = %s"
            params.append(beneficiary_id)
            
        payments_data = db.execute_query(query, params)
        
        # Transform database results to match the expected structure
        payments = []
        for payment in payments_data:
            payments.append({
                "payment_id": payment["payment_id"],
                "amount": float(payment["amount"]),
                "currency": payment["currency"],
                "beneficiary_id": payment["beneficiary_id"],
                "source_account_id": payment["source_account_id"],
                "status": PaymentStatus(payment["status"].lower()),
                "type": PaymentType(payment["type"].lower()),
                "scheduled_date": payment["scheduled_date"],
                "created_at": payment["created_at"],
                "completed_at": payment["completed_at"]
            })
            
        return payments
        
    except Exception as e:
        logger.error(f"Error fetching payments: {str(e)}")
        raise

@banking_tool(
    description="Initiate a payment",
    request_model=PaymentRequest,
    response_model=PaymentResponse
)
def initiate_payment(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a payment with validation and database operations"""
    try:
        logger.info(f"Starting initiate_payment with request data: {request_data}")
        
        # Validate and prepare request
        request = PaymentRequest(**request_data)
        if not request.payment_id:
            request.payment_id = str(uuid.uuid4())
            logger.info(f"Generated new payment_id: {request.payment_id}")
        
        # 1. Verify beneficiary exists
        logger.info(f"Verifying beneficiary: {request.beneficiary_id}")
        beneficiary_query = "SELECT * FROM beneficiaries WHERE beneficiary_id = %s"
        try:
            beneficiary_result = db.execute_query(beneficiary_query, [request.beneficiary_id])
            if not beneficiary_result:
                logger.error(f"Beneficiary not found: {request.beneficiary_id}")
                raise ValueError(f"Beneficiary with ID {request.beneficiary_id} does not exist")
            beneficiary = beneficiary_result[0]
            logger.info(f"Found beneficiary: {beneficiary}")
        except Exception as e:
            logger.error(f"Error verifying beneficiary: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to verify beneficiary: {str(e)}")
        
        # 2. Verify source account exists and has sufficient balance
        logger.info(f"Verifying source account: {request.source_account_id}")
        source_account_query = "SELECT * FROM accounts WHERE account_id = %s"
        try:
            source_account_result = db.execute_query(source_account_query, [request.source_account_id])
            if not source_account_result:
                logger.error(f"Source account not found: {request.source_account_id}")
                raise ValueError(f"Source account with ID {request.source_account_id} does not exist")
            source_account = source_account_result[0]
            logger.info(f"Found source account: {source_account}")
        except Exception as e:
            logger.error(f"Error verifying source account: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to verify source account: {str(e)}")
        
        # 3. Check if source account has sufficient balance
        if float(source_account['balance']) < float(request.amount):
            logger.error(f"Insufficient funds in account {request.source_account_id}. Balance: {source_account['balance']}, Required: {request.amount}")
            raise ValueError(f"Insufficient funds in account {request.source_account_id}. Current balance: {source_account['balance']}, Required amount: {request.amount}")
        
        # 4. Prepare payment record
        logger.info("Creating payment record")
        payment = Payment(
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency,
            beneficiary_id=request.beneficiary_id,
            source_account_id=request.source_account_id,
            status=PaymentStatus.COMPLETED,
            type=request.type,
            scheduled_date=request.scheduled_date,
            created_at=request.created_at or datetime.now(),
            completed_at=datetime.now()
        )
        
        # 5. Prepare transaction queries
        update_source_query = """
            UPDATE accounts 
            SET balance = balance - %s 
            WHERE account_id = %s
        """
        
        insert_payment_query = """
            INSERT INTO payments 
            (payment_id, amount, currency, beneficiary_id, source_account_id, status, `type`, scheduled_date, created_at, completed_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Prepare parameters for both queries
        update_params = [request.amount, request.source_account_id]
        insert_params = [
            payment.payment_id,
            payment.amount,
            payment.currency,
            payment.beneficiary_id,
            payment.source_account_id,
            payment.status.value,
            payment.type.value,
            None,  # scheduled_date
            payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            payment.completed_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        # Prepare transaction queries
        transaction_queries = [
            {
                'query': update_source_query,
                'params': update_params,
                'type': 'UPDATE'
            },
            {
                'query': insert_payment_query,
                'params': insert_params,
                'type': 'INSERT'
            }
        ]
        
        # 6. Execute transaction
        try:
            logger.info("Executing payment transaction...")
            result = db.execute_transaction(transaction_queries)
            
            if result['transaction_success']:
                logger.info("Payment transaction completed successfully")
                logger.info(f"Payment inserted with ID: {result['lastrowid']}")
                
                # Verify both operations affected the expected number of rows
                update_result = result['results'][0]
                insert_result = result['results'][1]
                
                if update_result['affected_rows'] != 1:
                    logger.warning(f"Expected 1 account to be updated, but got {update_result['affected_rows']}")
                if insert_result['affected_rows'] != 1:
                    logger.warning(f"Expected 1 payment to be inserted, but got {insert_result['affected_rows']}")
                    
            else:
                raise ValueError("Transaction failed to complete successfully")
                
        except ValueError as e:
            logger.error(f"Payment transaction failed: {str(e)}")
            raise
        
        # 7. Return response
        response = PaymentResponse(**payment.model_dump())
        logger.info("Payment processed successfully")
        return response.model_dump(mode='json')
            
    except Exception as e:
        logger.error(f"Error in initiate_payment: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid payment data: {str(e)}")

@banking_tool(
    description="List all beneficiaries",
    response_model=List[Beneficiary]
)
def list_beneficiaries() -> List[Dict[str, Any]]:
    """List all beneficiaries"""
    try:
        # Fetch beneficiaries from database
        query = "SELECT * FROM beneficiaries"
        beneficiaries_data = db.execute_query(query)
        
        # Transform database results to match the expected structure
        beneficiaries = []
        for ben in beneficiaries_data:
            beneficiaries.append({
                "beneficiary_id": ben["beneficiary_id"],
                "name": ben["name"],
                "account_number": ben["account_number"],
                "bank_code": ben["bank_code"],
                "created_at": ben["created_at"]
            })
            
        return beneficiaries
        
    except Exception as e:
        logger.error(f"Error fetching beneficiaries: {str(e)}")
        raise

@banking_tool(
    description="Create a new beneficiary",
    request_model=BeneficiaryRequest,
    response_model=BeneficiaryResponse
)
def create_beneficiary(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new beneficiary with validation and database insertion"""
    try:
        # Validate and prepare request
        request = BeneficiaryRequest(**request_data)
        beneficiary_id = request.beneficiary_id if request.beneficiary_id else str(uuid.uuid4())
        logger.info(f"Creating new beneficiary with ID: {beneficiary_id}")
        
        # Create beneficiary object
        beneficiary = Beneficiary(
            beneficiary_id=beneficiary_id,
            name=request.name,
            account_number=request.account_number,
            bank_code=request.bank_code,
            created_at=request.created_at
        )
        
        # Prepare insert query
        insert_beneficiary_query = """
            INSERT INTO beneficiaries 
            (beneficiary_id, name, account_number, bank_code, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Prepare parameters
        insert_params = [
            beneficiary.beneficiary_id,
            beneficiary.name,
            beneficiary.account_number,
            beneficiary.bank_code,
            beneficiary.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        # Prepare transaction query
        transaction_queries = [
            {
                'query': insert_beneficiary_query,
                'params': insert_params,
                'type': 'INSERT'
            }
        ]
        
        # Execute transaction
        try:
            logger.info("Executing beneficiary creation transaction...")
            result = db.execute_transaction(transaction_queries)
            
            if result['transaction_success']:
                logger.info("Beneficiary created successfully")
                logger.info(f"Beneficiary inserted with ID: {result['lastrowid']}")
                
                # Verify the insert affected one row
                insert_result = result['results'][0]
                if insert_result['affected_rows'] != 1:
                    logger.warning(f"Expected 1 beneficiary to be inserted, but got {insert_result['affected_rows']}")
                
                # Convert to response model
                response = BeneficiaryResponse(**beneficiary.model_dump())
                return response.model_dump(mode='json')
            else:
                raise ValueError("Beneficiary creation failed to complete successfully")
                
        except ValueError as e:
            logger.error(f"Beneficiary creation transaction failed: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error in create_beneficiary: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid beneficiary data: {str(e)}")

class BankingToolRegistry:
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Auto-register all functions with @banking_tool decorator"""
        import inspect
        current_module = inspect.getmodule(inspect.currentframe())
        
        for name, obj in inspect.getmembers(current_module):
            if inspect.isfunction(obj) and hasattr(obj, '_tool_description'):
                self.tools[name] = {
                    'function': obj,
                    'description': obj._tool_description,
                    'request_model': obj._request_model,
                    'response_model': obj._response_model
                }
    
    def get_tool_documentation(self) -> Dict[str, Any]:
        """Generate OpenAPI-style documentation"""
        docs = {"tools": {}}
        
        for name, tool in self.tools.items():
            tool_doc = {
                "description": tool['description'],
                "parameters": {}
            }
            
            if tool['request_model']:
                tool_doc["parameters"] = tool['request_model'].model_json_schema()
            
            if tool['response_model']:
                if get_origin(tool['response_model']) is list:
                    inner_type = get_args(tool['response_model'])[0]
                    if hasattr(inner_type, 'model_json_schema'):
                        tool_doc["returns"] = {
                            "type": "array",
                            "items": inner_type.model_json_schema()
                        }
                    else:
                        tool_doc["returns"] = {
                            "type": "array", 
                            "items": {"type": "object"}
                        }
                elif hasattr(tool['response_model'], 'model_json_schema'):
                    tool_doc["returns"] = tool['response_model'].model_json_schema()
                else:
                    tool_doc["returns"] = {"type": "object"}
            
            docs["tools"][name] = tool_doc
        
        return docs
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with validation"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        
        try:
            result = tool['function'](**kwargs)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"status": "error", "message": str(e)}

# Initialize registry
registry = BankingToolRegistry()

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    logger.info("Received event: %s", json.dumps(event))
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
    
    # Handle OPTIONS request for CORS
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Get the path from the event
        path = event.get('rawPath', '')
        if not path.startswith('/'):
            path = '/' + path
            
        # Get request body
        body = {}
        if event.get('requestBody', {}).get('content', {}).get('application/json', {}).get('properties'):
            # Handle Bedrock Agent's structured request body
            properties = event['requestBody']['content']['application/json']['properties']
            body = {prop['name']: prop['value'] for prop in properties}
            logger.info("Extracted request body from properties: %s", json.dumps(body))
        elif event.get('body'):
            try:
                body = json.loads(event['body'])
                logger.info("Request body: %s", json.dumps(body))
            except json.JSONDecodeError:
                logger.error("Invalid JSON in request body")
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'toolUseId': event.get('toolUseId', 'unknown'),
                        'status': 'error',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'Invalid JSON in request body'
                            }
                        ]
                    })
                }
        
        # Handle Bedrock Agent requests
        if 'agent' in event and 'apiPath' in event:
            api_path = event['apiPath']
            http_method = event.get('httpMethod', 'POST')
            action_group = event.get('actionGroup', 'toollist')
            
            # Extract toolUseId from the request
            tool_use_id = f"tooluse_{event.get('sessionId', 'unknown')}"
            
            # Map paths to internal functions
            path_mapping = {
                '/list_accounts': list_accounts,
                '/create_account': create_account,
                '/list_payments': list_payments,
                '/initiate_payment': initiate_payment,
                '/list_beneficiaries': list_beneficiaries,
                '/create_beneficiary': create_beneficiary
            }
            
            if api_path in path_mapping:
                try:
                    # For list_accounts, we don't need any parameters
                    if api_path in ['/list_accounts', '/list_beneficiaries', '/list_payments']:
                        result = path_mapping[api_path]()
                    else:
                        result = path_mapping[api_path](request_data=body)
                    
                    # Format response for Bedrock Agent in the expected format
                    bedrock_response = {
                        "messageVersion": "1.0",
                        "response": {
                            "actionGroup": event.get('actionGroup', 'toollist'),
                            "apiPath": api_path,
                            "httpMethod": event.get('httpMethod', 'POST'),
                            "httpStatusCode": 200,
                            "responseBody": {
                                "application/json": {
                                    "body": json.dumps(result, default=str)  # Use default=str for datetime serialization
                                }
                            }
                        }
                    }
                    logger.info("Bedrock Agent response: %s", json.dumps(bedrock_response))
                    return bedrock_response
                except Exception as e:
                    error_response = {
                        "messageVersion": "1.0",
                        "response": {
                            "actionGroup": event.get('actionGroup', 'toollist'),
                            "apiPath": api_path,
                            "httpMethod": event.get('httpMethod', 'POST'),
                            "httpStatusCode": 500,
                            "responseBody": {
                                "application/json": {
                                    "body": json.dumps({
                                        "error": str(e),
                                        "message": f"Failed to execute {api_path}"
                                    }, default=str)  # Use default=str for datetime serialization
                                }
                            }
                        }
                    }
                    logger.error("Error executing path %s: %s", api_path, str(e))
                    return error_response
            else:
                error_response = {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'toolUseId': tool_use_id,
                        'status': 'error',
                        'content': [
                            {
                                'type': 'text',
                                'text': f'Unknown path: {api_path}'
                            }
                        ]
                    }, default=str)  # Use default=str for datetime serialization
                }
                return error_response
        
        # Handle direct API requests
        if path == '/list_accounts':
            result = list_accounts()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        elif path == '/create_account':
            if not body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'Request body is required'
                    }, default=str)  # Use default=str for datetime serialization
                }
            result = create_account(**body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        elif path == '/list_payments':
            if 'beneficiary_id' in body:
                result = list_payments(body['beneficiary_id'])
            else:
                result = list_payments()
            return {
                'statusCode': 200, 
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        elif path == '/initiate_payment':
            if not body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'Request body is required'
                    }, default=str)  # Use default=str for datetime serialization
                }
            result = initiate_payment(**body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        elif path == '/list_beneficiaries':
            result = list_beneficiaries()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        elif path == '/create_beneficiary':
            if not body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'Request body is required'
                    }, default=str)  # Use default=str for datetime serialization
                }
            result = create_beneficiary(body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                }, default=str)  # Use default=str for datetime serialization
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': f'Not found: {path}. Available paths: /list_accounts, /create_account, /list_payments, /initiate_payment, /list_beneficiaries, /create_beneficiary'
                }, default=str)  # Use default=str for datetime serialization
            }
            
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            }, default=str)  # Use default=str for datetime serialization
        } 