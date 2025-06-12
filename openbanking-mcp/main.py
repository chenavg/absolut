# server.py
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum
from db_config import get_db_connection, init_db

# Create an MCP server
mcp = FastMCP("OpenBankingDemo")

# Initialize database
init_db()

# Data models
class AccountType(Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    INVESTMENT = "INVESTMENT"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"

class Account:
    def __init__(self, account_id: str, account_type: str, balance: float, currency: str):
        self.account_id = account_id
        self.account_type = account_type
        self.balance = balance
        self.currency = currency
        self.created_at = datetime.now().isoformat()

class Beneficiary:
    def __init__(self, beneficiary_id: str, name: str, account_number: str, bank_code: str):
        self.beneficiary_id = beneficiary_id
        self.name = name
        self.account_number = account_number
        self.bank_code = bank_code

class Payment:
    def __init__(self, payment_id: str, amount: float, currency: str, beneficiary_id: str, 
                 status: str, scheduled_date: Optional[datetime] = None):
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
        self.beneficiary_id = beneficiary_id
        self.status = status
        self.scheduled_date = scheduled_date

# Mock database for other entities (to be migrated later)
beneficiaries_db: Dict[str, Dict] = {}
payments_db: Dict[str, Payment] = {}

# Account Management
@mcp.tool()
def list_accounts(
    account_type: Optional[str] = None,
    currency: Optional[str] = None,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None,
    sort_by: Optional[str] = "balance",
    sort_order: Optional[str] = "desc"
) -> List[Dict]:
    """List all accounts with filtering and sorting options
    
    Args:
        account_type: Filter by account type (e.g., "SAVINGS", "CHECKING")
        currency: Filter by currency code (e.g., "USD", "EUR")
        min_balance: Filter by minimum balance
        max_balance: Filter by maximum balance
        sort_by: Sort field ("balance", "created_at", "account_type")
        sort_order: Sort order ("asc" or "desc")
        
    Returns:
        List of accounts matching the criteria
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Build the query
        query = "SELECT * FROM accounts WHERE 1=1"
        params = []
        
        if account_type:
            query += " AND account_type = %s"
            params.append(account_type)
        
        if currency:
            query += " AND currency = %s"
            params.append(currency)
        
        if min_balance is not None:
            query += " AND balance >= %s"
            params.append(min_balance)
        
        if max_balance is not None:
            query += " AND balance <= %s"
            params.append(max_balance)
        
        # Add sorting
        if sort_by in ["balance", "created_at", "account_type"]:
            query += f" ORDER BY {sort_by} {'DESC' if sort_order.lower() == 'desc' else 'ASC'}"
        
        cursor.execute(query, params)
        accounts = cursor.fetchall()
        
        # Convert datetime objects to ISO format strings
        for account in accounts:
            account['created_at'] = account['created_at'].isoformat()
        
        return accounts
    except Error as e:
        print(f"Error listing accounts: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def get_account_summary() -> Dict:
    """Get a summary of all accounts including total balance by currency and account type
    
    Returns:
        Dictionary containing account summary statistics
    """
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get total accounts
        cursor.execute("SELECT COUNT(*) as total FROM accounts")
        total_accounts = cursor.fetchone()['total']
        
        # Get balance by currency
        cursor.execute("""
            SELECT currency, SUM(balance) as total_balance 
            FROM accounts 
            GROUP BY currency
        """)
        balance_by_currency = {row['currency']: float(row['total_balance']) for row in cursor.fetchall()}
        
        # Get accounts by type
        cursor.execute("""
            SELECT account_type, COUNT(*) as count 
            FROM accounts 
            GROUP BY account_type
        """)
        accounts_by_type = {row['account_type']: row['count'] for row in cursor.fetchall()}
        
        return {
            "total_accounts": total_accounts,
            "balance_by_currency": balance_by_currency,
            "accounts_by_type": accounts_by_type,
            "last_updated": datetime.now().isoformat()
        }
    except Error as e:
        print(f"Error getting account summary: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def add_account(account_type: str, balance: float, currency: str) -> Dict:
    """Add a single bank account
    
    Args:
        account_type: Type of account (e.g., "SAVINGS", "CHECKING")
        balance: Initial balance
        currency: Currency code (e.g., "USD", "EUR")
        
    Returns:
        Dictionary containing the created account details
    """
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        account_id = str(uuid4())
        created_at = datetime.now()
        
        cursor.execute("""
            INSERT INTO accounts (account_id, account_type, balance, currency, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (account_id, account_type, balance, currency, created_at))
        
        connection.commit()
        
        return {
            "account_id": account_id,
            "account_type": account_type,
            "balance": balance,
            "currency": currency,
            "created_at": created_at.isoformat()
        }
    except Error as e:
        print(f"Error adding account: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def add_multiple_accounts(accounts: List[Dict]) -> List[Dict]:
    """Add multiple bank accounts at once
    
    Args:
        accounts: List of account details, each containing:
            - account_type: Type of account (e.g., "SAVINGS", "CHECKING")
            - balance: Initial balance
            - currency: Currency code (e.g., "USD", "EUR")
            
    Returns:
        List of created accounts with their details
    """
    connection = get_db_connection()
    if not connection:
        return [{"error": "Database connection failed"}]
    
    try:
        cursor = connection.cursor()
        created_accounts = []
        
        for account_data in accounts:
            account_id = str(uuid4())
            created_at = datetime.now()
            
            cursor.execute("""
                INSERT INTO accounts (account_id, account_type, balance, currency, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                account_id,
                account_data["account_type"],
                account_data["balance"],
                account_data["currency"],
                created_at
            ))
            
            created_accounts.append({
                "account_id": account_id,
                "account_type": account_data["account_type"],
                "balance": account_data["balance"],
                "currency": account_data["currency"],
                "created_at": created_at.isoformat()
            })
        
        connection.commit()
        return created_accounts
    except Error as e:
        print(f"Error adding multiple accounts: {e}")
        return [{"error": str(e)}]
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@mcp.resource("accounts://{customer_id}")
def get_accounts(customer_id: str) -> List[Dict]:
    """Get all accounts for a customer"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        
        # Convert datetime objects to ISO format strings
        for account in accounts:
            account['created_at'] = account['created_at'].isoformat()
        
        return accounts
    except Error as e:
        print(f"Error getting accounts: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@mcp.resource("account://{account_id}")
def get_account_details(account_id: str) -> Dict:
    """Get detailed information about a specific account"""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {"error": "Account not found"}
        
        account['created_at'] = account['created_at'].isoformat()
        return account
    except Error as e:
        print(f"Error getting account details: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Beneficiary Management
@mcp.tool()
def add_beneficiary(name: str, account_number: str, bank_code: str) -> Dict:
    """Add a new beneficiary"""
    beneficiary_id = str(uuid4())
    beneficiaries_db[beneficiary_id] = {
        "beneficiary_id": beneficiary_id,
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code
    }
    return beneficiaries_db[beneficiary_id]

@mcp.tool()
def delete_beneficiary(beneficiary_id: str) -> Dict:
    """Delete a beneficiary"""
    if beneficiary_id in beneficiaries_db:
        del beneficiaries_db[beneficiary_id]
        return {"status": "success", "message": "Beneficiary deleted successfully"}
    return {"status": "error", "message": "Beneficiary not found"}

@mcp.resource("beneficiaries://{customer_id}")
def get_beneficiaries(customer_id: str) -> List[Dict]:
    """Get all beneficiaries for a customer"""
    return list(beneficiaries_db.values())

@mcp.tool()
def search_beneficiaries(name: Optional[str] = None, bank_code: Optional[str] = None) -> List[Dict]:
    """Search beneficiaries by name or bank code
    
    Args:
        name: Optional name to search for (case-insensitive partial match)
        bank_code: Optional bank code to search for (exact match)
        
    Returns:
        List of matching beneficiaries
    """
    results = list(beneficiaries_db.values())
    
    if name:
        # Case-insensitive partial name match
        results = [b for b in results if name.lower() in b["name"].lower()]
    
    if bank_code:
        # Exact bank code match
        results = [b for b in results if b["bank_code"] == bank_code]
    
    return results

# Payment Operations
@mcp.tool()
def initiate_payment(amount: float, currency: str, beneficiary_id: str) -> Dict:
    """Initiate an immediate payment"""
    if beneficiary_id not in beneficiaries_db:
        return {"status": "error", "message": "Beneficiary not found"}
    
    payment_id = str(uuid4())
    payment = {
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency,
        "beneficiary_id": beneficiary_id,
        "status": "PENDING",
        "type": "IMMEDIATE",
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    payments_db[payment_id] = payment
    return payment

@mcp.tool()
def schedule_payment(amount: float, currency: str, beneficiary_id: str, 
                    scheduled_date: datetime) -> Dict:
    """Schedule a future payment"""
    if beneficiary_id not in beneficiaries_db:
        return {"status": "error", "message": "Beneficiary not found"}
    
    payment_id = str(uuid4())
    payment = {
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency,
        "beneficiary_id": beneficiary_id,
        "status": "SCHEDULED",
        "type": "SCHEDULED",
        "scheduled_date": scheduled_date.isoformat(),
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    payments_db[payment_id] = payment
    return payment

@mcp.tool()
def cancel_payment(payment_id: str) -> Dict:
    """Cancel a scheduled payment"""
    if payment_id not in payments_db:
        return {"status": "error", "message": "Payment not found"}
    
    payment = payments_db[payment_id]
    if payment["status"] != "SCHEDULED":
        return {"status": "error", "message": "Only scheduled payments can be cancelled"}
    
    payment["status"] = "CANCELLED"
    return {
        "payment_id": payment_id,
        "status": "CANCELLED",
        "message": "Payment cancelled successfully"
    }

@mcp.tool()
def search_payment_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    currency: Optional[str] = None,
    status: Optional[str] = None,
    payment_type: Optional[str] = None,
    beneficiary_id: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = None
) -> List[Dict]:
    """Search payment history with various filtering and sorting options
    
    Args:
        start_date: Filter payments created after this date
        end_date: Filter payments created before this date
        min_amount: Filter payments with amount greater than or equal to this
        max_amount: Filter payments with amount less than or equal to this
        currency: Filter payments in specific currency
        status: Filter by payment status (PENDING, COMPLETED, FAILED, CANCELLED, SCHEDULED)
        payment_type: Filter by payment type (IMMEDIATE, SCHEDULED, RECURRING)
        beneficiary_id: Filter payments to specific beneficiary
        sort_by: Sort field ("created_at", "amount", "scheduled_date")
        sort_order: Sort order ("asc" or "desc")
        limit: Maximum number of results to return
        
    Returns:
        List of payments matching the criteria
    """
    # Get all payments
    payments = list(payments_db.values())
    
    # Apply filters
    if start_date:
        payments = [p for p in payments if datetime.fromisoformat(p["created_at"]) >= start_date]
    
    if end_date:
        payments = [p for p in payments if datetime.fromisoformat(p["created_at"]) <= end_date]
    
    if min_amount is not None:
        payments = [p for p in payments if p["amount"] >= min_amount]
    
    if max_amount is not None:
        payments = [p for p in payments if p["amount"] <= max_amount]
    
    if currency:
        payments = [p for p in payments if p["currency"] == currency]
    
    if status:
        payments = [p for p in payments if p["status"] == status]
    
    if payment_type:
        payments = [p for p in payments if p["type"] == payment_type]
    
    if beneficiary_id:
        payments = [p for p in payments if p["beneficiary_id"] == beneficiary_id]
    
    # Apply sorting
    reverse = sort_order.lower() == "desc"
    if sort_by == "created_at":
        payments.sort(key=lambda x: x["created_at"], reverse=reverse)
    elif sort_by == "amount":
        payments.sort(key=lambda x: x["amount"], reverse=reverse)
    elif sort_by == "scheduled_date":
        payments.sort(key=lambda x: x.get("scheduled_date", ""), reverse=reverse)
    
    # Apply limit
    if limit is not None:
        payments = payments[:limit]
    
    return payments

@mcp.tool()
def get_payment_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """Get payment statistics for a given date range
    
    Args:
        start_date: Start date for statistics
        end_date: End date for statistics
        
    Returns:
        Dictionary containing payment statistics
    """
    payments = list(payments_db.values())
    
    # Apply date filters if provided
    if start_date:
        payments = [p for p in payments if datetime.fromisoformat(p["created_at"]) >= start_date]
    if end_date:
        payments = [p for p in payments if datetime.fromisoformat(p["created_at"]) <= end_date]
    
    # Calculate statistics
    total_payments = len(payments)
    total_amount = sum(p["amount"] for p in payments)
    
    # Count by status
    status_counts = {}
    for p in payments:
        status = p["status"]
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    # Count by currency
    currency_amounts = {}
    for p in payments:
        currency = p["currency"]
        if currency not in currency_amounts:
            currency_amounts[currency] = 0
        currency_amounts[currency] += p["amount"]
    
    # Count by payment type
    type_counts = {}
    for p in payments:
        payment_type = p["type"]
        if payment_type not in type_counts:
            type_counts[payment_type] = 0
        type_counts[payment_type] += 1
    
    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "status_breakdown": status_counts,
        "currency_breakdown": currency_amounts,
        "type_breakdown": type_counts,
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        },
        "last_updated": datetime.now().isoformat()
    }

@mcp.resource("payments://{customer_id}")
def get_payments(customer_id: str) -> List[Dict]:
    """Get all payments for a customer"""
    return list(payments_db.values())

# Transaction History
@mcp.tool()
def get_transaction_history(account_id: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Dict]:
    """Get transaction history for an account with optional date filtering"""
    # This would typically query a transactions database
    # For demo purposes, returning mock data
    return [
        {
            "transaction_id": str(uuid4()),
            "date": datetime.now().isoformat(),
            "amount": 100.00,
            "type": "CREDIT",
            "description": "Sample transaction"
        }
    ]

# Balance Check
@mcp.resource("balance://{account_id}")
def get_account_balance(account_id: str) -> Dict:
    """Get current balance for an account"""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT account_id, balance, currency 
            FROM accounts 
            WHERE account_id = %s
        """, (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {"error": "Account not found"}
        
        return {
            "account_id": account['account_id'],
            "balance": float(account['balance']),
            "currency": account['currency'],
            "last_updated": datetime.now().isoformat()
        }
    except Error as e:
        print(f"Error getting account balance: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()