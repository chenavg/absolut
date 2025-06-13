# server.py
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum
from database import db

# Create an MCP server
mcp = FastMCP("OpenBankingDemo")

# Initialize database tables
db.initialize_tables()

# Data models
class AccountType(Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    INVESTMENT = "INVESTMENT"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"

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
    """List all accounts with filtering and sorting options"""
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
    
    query += f" ORDER BY {sort_by} {sort_order}"
    
    return db.execute_query(query, params)

@mcp.tool()
def get_account_summary() -> Dict:
    """Get a summary of all accounts including total balance by currency and account type"""
    balance_query = """
        SELECT currency, SUM(balance) as total_balance
        FROM accounts
        GROUP BY currency
    """
    
    type_query = """
        SELECT account_type, COUNT(*) as count
        FROM accounts
        GROUP BY account_type
    """
    
    balance_by_currency = {row['currency']: float(row['total_balance']) 
                          for row in db.execute_query(balance_query)}
    
    accounts_by_type = {row['account_type']: row['count'] 
                       for row in db.execute_query(type_query)}
    
    total_accounts = sum(accounts_by_type.values())
    
    return {
        "total_accounts": total_accounts,
        "balance_by_currency": balance_by_currency,
        "accounts_by_type": accounts_by_type,
        "last_updated": datetime.now().isoformat()
    }

@mcp.tool()
def add_account(account_type: str, balance: float, currency: str) -> Dict:
    """Add a single bank account"""
    account_id = str(uuid4())
    query = """
        INSERT INTO accounts (account_id, account_type, balance, currency)
        VALUES (%s, %s, %s, %s)
    """
    params = (account_id, account_type, balance, currency)
    
    db.execute_update(query, params)
    
    return {
        "account_id": account_id,
        "account_type": account_type,
        "balance": balance,
        "currency": currency,
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def add_multiple_accounts(accounts: List[Dict]) -> List[Dict]:
    """Add multiple bank accounts at once"""
    created_accounts = []
    
    for account_data in accounts:
        account_id = str(uuid4())
        query = """
            INSERT INTO accounts (account_id, account_type, balance, currency)
            VALUES (%s, %s, %s, %s)
        """
        params = (
            account_id,
            account_data["account_type"],
            account_data["balance"],
            account_data["currency"]
        )
        
        db.execute_update(query, params)
        
        created_accounts.append({
            "account_id": account_id,
            "account_type": account_data["account_type"],
            "balance": account_data["balance"],
            "currency": account_data["currency"],
            "created_at": datetime.now().isoformat()
        })
    
    return created_accounts

@mcp.resource("accounts://{customer_id}")
def get_accounts(customer_id: str) -> List[Dict]:
    """Get all accounts for a customer"""
    query = "SELECT * FROM accounts"
    return db.execute_query(query)

@mcp.resource("account://{account_id}")
def get_account_details(account_id: str) -> Dict:
    """Get detailed information about a specific account"""
    query = "SELECT * FROM accounts WHERE account_id = %s"
    result = db.execute_query(query, (account_id,))
    
    if not result:
        return {"error": "Account not found"}
    return result[0]

# Beneficiary Management
@mcp.tool()
def add_beneficiary(name: str, account_number: str, bank_code: str) -> Dict:
    """Add a new beneficiary"""
    beneficiary_id = str(uuid4())
    query = """
        INSERT INTO beneficiaries (beneficiary_id, name, account_number, bank_code)
        VALUES (%s, %s, %s, %s)
    """
    params = (beneficiary_id, name, account_number, bank_code)
    
    db.execute_update(query, params)
    
    return {
        "beneficiary_id": beneficiary_id,
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code,
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def delete_beneficiary(beneficiary_id: str) -> Dict:
    """Delete a beneficiary"""
    query = "DELETE FROM beneficiaries WHERE beneficiary_id = %s"
    affected_rows = db.execute_update(query, (beneficiary_id,))
    
    if affected_rows > 0:
        return {"status": "success", "message": "Beneficiary deleted successfully"}
    return {"status": "error", "message": "Beneficiary not found"}

@mcp.resource("beneficiaries://{customer_id}")
def get_beneficiaries(customer_id: str) -> List[Dict]:
    """Get all beneficiaries for a customer"""
    query = "SELECT * FROM beneficiaries"
    return db.execute_query(query)

@mcp.tool()
def search_beneficiaries(name: Optional[str] = None, bank_code: Optional[str] = None) -> List[Dict]:
    """Search beneficiaries by name or bank code"""
    query = "SELECT * FROM beneficiaries WHERE 1=1"
    params = []
    
    if name:
        query += " AND LOWER(name) LIKE LOWER(%s)"
        params.append(f"%{name}%")
    
    if bank_code:
        query += " AND bank_code = %s"
        params.append(bank_code)
    
    return db.execute_query(query, params)

# Payment Operations
@mcp.tool()
def initiate_payment(amount: float, currency: str, beneficiary_id: str) -> Dict:
    """Initiate an immediate payment"""
    # Check if beneficiary exists
    beneficiary_query = "SELECT * FROM beneficiaries WHERE beneficiary_id = %s"
    beneficiary = db.execute_query(beneficiary_query, (beneficiary_id,))
    
    if not beneficiary:
        return {"status": "error", "message": "Beneficiary not found"}
    
    payment_id = str(uuid4())
    query = """
        INSERT INTO payments (payment_id, amount, currency, beneficiary_id, status, type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (payment_id, amount, currency, beneficiary_id, "PENDING", "IMMEDIATE")
    
    db.execute_update(query, params)
    
    return {
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency,
        "beneficiary_id": beneficiary_id,
        "status": "PENDING",
        "type": "IMMEDIATE",
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def schedule_payment(amount: float, currency: str, beneficiary_id: str, 
                    scheduled_date: datetime) -> Dict:
    """Schedule a future payment"""
    # Check if beneficiary exists
    beneficiary_query = "SELECT * FROM beneficiaries WHERE beneficiary_id = %s"
    beneficiary = db.execute_query(beneficiary_query, (beneficiary_id,))
    
    if not beneficiary:
        return {"status": "error", "message": "Beneficiary not found"}
    
    payment_id = str(uuid4())
    query = """
        INSERT INTO payments (payment_id, amount, currency, beneficiary_id, status, type, scheduled_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (payment_id, amount, currency, beneficiary_id, "SCHEDULED", "SCHEDULED", scheduled_date)
    
    db.execute_update(query, params)
    
    return {
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency,
        "beneficiary_id": beneficiary_id,
        "status": "SCHEDULED",
        "type": "SCHEDULED",
        "scheduled_date": scheduled_date.isoformat(),
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def cancel_payment(payment_id: str) -> Dict:
    """Cancel a scheduled payment"""
    query = """
        UPDATE payments 
        SET status = 'CANCELLED'
        WHERE payment_id = %s AND status = 'SCHEDULED'
    """
    affected_rows = db.execute_update(query, (payment_id,))
    
    if affected_rows > 0:
        return {
            "payment_id": payment_id,
            "status": "CANCELLED",
            "message": "Payment cancelled successfully"
        }
    return {"status": "error", "message": "Payment not found or cannot be cancelled"}

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
    """Search payment history with various filtering and sorting options"""
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND created_at >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND created_at <= %s"
        params.append(end_date)
    
    if min_amount is not None:
        query += " AND amount >= %s"
        params.append(min_amount)
    
    if max_amount is not None:
        query += " AND amount <= %s"
        params.append(max_amount)
    
    if currency:
        query += " AND currency = %s"
        params.append(currency)
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    if payment_type:
        query += " AND type = %s"
        params.append(payment_type)
    
    if beneficiary_id:
        query += " AND beneficiary_id = %s"
        params.append(beneficiary_id)
    
    query += f" ORDER BY {sort_by} {sort_order}"
    
    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    
    return db.execute_query(query, params)

@mcp.tool()
def get_payment_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """Get payment statistics for a given date range"""
    where_clause = "WHERE 1=1"
    params = []
    
    if start_date:
        where_clause += " AND created_at >= %s"
        params.append(start_date)
    if end_date:
        where_clause += " AND created_at <= %s"
        params.append(end_date)
    
    total_query = f"""
        SELECT COUNT(*) as total_payments,
               SUM(amount) as total_amount
        FROM payments
        {where_clause}
    """
    
    status_query = f"""
        SELECT status, COUNT(*) as count
        FROM payments
        {where_clause}
        GROUP BY status
    """
    
    currency_query = f"""
        SELECT currency, SUM(amount) as total_amount
        FROM payments
        {where_clause}
        GROUP BY currency
    """
    
    type_query = f"""
        SELECT type, COUNT(*) as count
        FROM payments
        {where_clause}
        GROUP BY type
    """
    
    total_stats = db.execute_query(total_query, params)[0]
    status_counts = {row['status']: row['count'] for row in db.execute_query(status_query, params)}
    currency_amounts = {row['currency']: float(row['total_amount']) 
                       for row in db.execute_query(currency_query, params)}
    type_counts = {row['type']: row['count'] for row in db.execute_query(type_query, params)}
    
    return {
        "total_payments": total_stats['total_payments'],
        "total_amount": float(total_stats['total_amount'] or 0),
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
    query = "SELECT * FROM payments"
    return db.execute_query(query)

# Balance Check
@mcp.resource("balance://{account_id}")
def get_account_balance(account_id: str) -> Dict:
    """Get current balance for an account"""
    query = "SELECT account_id, balance, currency FROM accounts WHERE account_id = %s"
    result = db.execute_query(query, (account_id,))
    
    if not result:
        return {"error": "Account not found"}
    
    account = result[0]
    return {
        "account_id": account['account_id'],
        "balance": float(account['balance']),
        "currency": account['currency'],
        "last_updated": datetime.now().isoformat()
    } 