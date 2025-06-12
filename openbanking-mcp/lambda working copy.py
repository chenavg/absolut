from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, get_origin, get_args
from enum import Enum
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define request/response models
class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

class Account(BaseModel):
    id: str = Field(..., description="Unique account identifier")
    name: str = Field(..., description="Account name")
    type: AccountType = Field(..., description="Type of account")
    balance: float = Field(..., description="Current account balance")
    currency: str = Field(default="USD", description="Account currency")

class CreateAccountRequest(BaseModel):
    name: str = Field(..., description="Account name", min_length=1, max_length=100)
    type: AccountType = Field(..., description="Type of account to create")
    initial_balance: float = Field(default=0.0, description="Initial account balance", ge=0)
    currency: str = Field(default="USD", description="Account currency", pattern="^[A-Z]{3}$")

class PaymentRequest(BaseModel):
    from_account: str = Field(..., description="Source account ID")
    to_account: str = Field(..., description="Destination account ID")
    amount: float = Field(..., description="Payment amount", gt=0)
    description: Optional[str] = Field(None, description="Payment description", max_length=200)
    
    @field_validator('to_account')
    @classmethod
    def validate_accounts_different(cls, v, info):
        if info.data.get('from_account') == v:
            raise ValueError('Source and destination accounts must be different')
        return v

class PaymentResponse(BaseModel):
    payment_id: str = Field(..., description="Unique payment identifier")
    status: str = Field(..., description="Payment status")
    from_account: str = Field(..., description="Source account ID")
    to_account: str = Field(..., description="Destination account ID")
    amount: float = Field(..., description="Payment amount")
    description: Optional[str] = Field(None, description="Payment description")

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
        # Mock data - replace with actual implementation
        accounts = [
            {
                "id": "acc_001",
                "name": "Primary Checking",
                "type": AccountType.CHECKING,
                "balance": 2500.50,
                "currency": "USD"
            },
            {
                "id": "acc_002",
                "name": "Savings Account",
                "type": AccountType.SAVINGS,
                "balance": 10000.00,
                "currency": "USD"
            },
        ]
        
        # Validate response against model
        validated_accounts = [Account(**acc) for acc in accounts]
        return [acc.model_dump() for acc in validated_accounts]
    except Exception as e:
        logger.error(f"Error in list_accounts: {str(e)}")
        raise

@banking_tool(
    description="Create a new bank account",
    request_model=CreateAccountRequest,
    response_model=Account
)
def create_account(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new bank account with validation"""
    try:
        request = CreateAccountRequest(**request_data)
        new_account = Account(
            id=f"acc_{len(list_accounts()) + 1:03d}",
            name=request.name,
            type=request.type,
            balance=request.initial_balance,
            currency=request.currency
        )
        return new_account.model_dump()
    except Exception as e:
        logger.error(f"Error in create_account: {str(e)}")
        raise ValueError(f"Invalid request data: {str(e)}")

@banking_tool(
    description="Initiate a payment between accounts",
    request_model=PaymentRequest,
    response_model=PaymentResponse
)
def initiate_payment(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a payment with validation"""
    try:
        payment = PaymentRequest(**request_data)
        response = PaymentResponse(
            payment_id="pay_001",
            status="completed",
            from_account=payment.from_account,
            to_account=payment.to_account,
            amount=payment.amount,
            description=payment.description
        )
        return response.model_dump()
    except Exception as e:
        logger.error(f"Error in initiate_payment: {str(e)}")
        raise ValueError(f"Invalid payment data: {str(e)}")

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
            
        # Get request body if present
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
            
            # Extract parameters from the request body
            body = {}
            if 'requestBody' in event and 'content' in event['requestBody']:
                content = event['requestBody']['content'].get('application/json', {})
                if 'properties' in content:
                    body = {prop['name']: prop['value'] for prop in content['properties']}
                    logger.info("Extracted request body from properties: %s", json.dumps(body))
            
            logger.info("Bedrock Agent request - Path: %s, Method: %s, Action Group: %s, Tool Use ID: %s", 
                       api_path, http_method, action_group, tool_use_id)
            
            # Map paths to internal functions
            path_mapping = {
                '/list_accounts': list_accounts,
                '/create_account': create_account,
                '/initiate_payment': initiate_payment
            }
            
            if api_path in path_mapping:
                try:
                    # For list_accounts, we don't need any parameters
                    if api_path == '/list_accounts':
                        result = path_mapping[api_path]()  # Remove **body since we don't need parameters
                    else:
                        result = path_mapping[api_path](**body)
                    
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
                                    "body": json.dumps({
                                        "accounts": result,
                                        "message": "Successfully retrieved accounts"
                                    })
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
                                        "message": "Failed to retrieve accounts"
                                    })
                                }
                            }
                        }
                    }
                    logger.error("Error executing path %s: %s", api_path, str(e))
                    logger.error("Error response: %s", json.dumps(error_response))
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
                    })
                }
                logger.error("Unknown path: %s", api_path)
                logger.error("Error response: %s", json.dumps(error_response))
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
                })
            }
        elif path == '/create_account':
            if not body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'Request body is required'
                    })
                }
            result = create_account(**body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                })
            }
        elif path == '/initiate_payment':
            if not body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'Request body is required'
                    })
                }
            result = initiate_payment(**body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': f'Not found: {path}. Available paths: /list_accounts, /create_account, /initiate_payment'
                })
            }
            
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        } 