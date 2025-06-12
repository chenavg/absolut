# server.py
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum

# Create an MCP server
mcp = FastMCP("OpenBankingDemo")

# Data models
class AccountType(Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    INVESTMENT = "INVESTMENT"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"

class Account:
    def __init__(self, account_id: str, account_name: str, account_type: str, interest_rate: float, bank_code: str, balance: float, currency: str, country: str):
        self.account_id = account_id
        self.account_name = account_name
        self.account_type = account_type
        self.interest_rate = interest_rate
        self.bank_code = bank_code
        self.balance = balance
        self.currency = currency
        self.country = country
        self.created_at = datetime.now().isoformat()

class Beneficiary:
    def __init__(self, beneficiary_id: str, cust_account_id: str, name: str, ben_account_id: str, bank_code: str, currency: str, country: str):
        self.beneficiary_id = beneficiary_id
        self.ben_account_id = ben_account_id
        self.cust_account_id = cust_account_id
        self.name = name
        self.bank_code = bank_code
        self.currency = currency
        self.country = country
        

class Payment:
    def __init__(self, payment_id: str, amount: float, currency: str, beneficiary_id: str, 
                 status: str, scheduled_date: Optional[datetime] = None):
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
        self.beneficiary_id = beneficiary_id
        self.status = status
        self.scheduled_date = scheduled_date

# Mock database
accounts_db: Dict[str, Account] = {}
beneficiaries_db: Dict[str, Dict] = {}
payments_db: Dict[str, Payment] = {}
blocked_currencies_db = {"RUB","SYP","IRR","VES","SDG","CUP"}

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
    # Convert accounts to list of dictionaries
    accounts = [
        {
            "account_id": acc.account_id,
            "account_name": acc.account_name,
            "interest_rate": acc.interest_rate,
            "bank_code": acc.bank_code,
            "country": acc.country,
            "account_type": acc.account_type,
            "balance": acc.balance,
            "currency": acc.currency,
            "created_at": acc.created_at
        }
        for acc in accounts_db.values()
    ]
    
    # Apply filters
    if account_type:
        accounts = [acc for acc in accounts if acc["account_type"] == account_type]
    
    if currency:
        accounts = [acc for acc in accounts if acc["currency"] == currency]
    
    if min_balance is not None:
        accounts = [acc for acc in accounts if acc["balance"] >= min_balance]
    
    if max_balance is not None:
        accounts = [acc for acc in accounts if acc["balance"] <= max_balance]
    
    # Apply sorting
    reverse = sort_order.lower() == "desc"
    if sort_by == "balance":
        accounts.sort(key=lambda x: x["balance"], reverse=reverse)
    elif sort_by == "created_at":
        accounts.sort(key=lambda x: x["created_at"], reverse=reverse)
    elif sort_by == "account_type":
        accounts.sort(key=lambda x: x["account_type"], reverse=reverse)
    
    return accounts

@mcp.tool()
def get_account_summary() -> Dict:
    """Get a summary of all accounts including total balance by currency and account type
    
    Returns:
        Dictionary containing account summary statistics
    """
    accounts = list(accounts_db.values())
    
    # Calculate total balance by currency
    balance_by_currency = {}
    for acc in accounts:
        if acc.currency not in balance_by_currency:
            balance_by_currency[acc.currency] = 0
        balance_by_currency[acc.currency] += acc.balance
    
    # Count accounts by type
    accounts_by_type = {}
    for acc in accounts:
        if acc.account_type not in accounts_by_type:
            accounts_by_type[acc.account_type] = 0
        accounts_by_type[acc.account_type] += 1
    
    return {
        "total_accounts": len(accounts),
        "balance_by_currency": balance_by_currency,
        "accounts_by_type": accounts_by_type,
        "last_updated": datetime.now().isoformat()
    }

@mcp.tool()
def add_account(account_type: str, balance: float, currency: str, interest_rate: float, bank_code: str, country: str, account_name: str) -> Dict:
    """Add a single bank account
    
    Args:
        account_type: Type of account (e.g., "SAVINGS", "CHECKING")
        balance: Initial balance
        currency: Currency code (e.g., "USD", "EUR")
        
    Returns:
        Dictionary containing the created account details
    """
    account_id = str(uuid4())
    account = Account(account_id, account_name, account_type, interest_rate, bank_code, balance, currency, country)
    accounts_db[account_id] = account
    return {
        "account_id": account_id,
        "account_type": account_type,
        "interest_rate": interest_rate,
        "bank_code": bank_code,
        "country": country,
        "account_name": account_name,
        "balance": balance,
        "currency": currency,
        "created_at": account.created_at
    }

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
    created_accounts = []
    
    for account_data in accounts:
        account_id = str(uuid4())
        account = Account(
            account_id,
            account_data["account_name"],
            account_data["account_type"],
            account_data["interest_rate"],
            account_data["bank_code"],
            account_data["balance"],
            account_data["currency"],
            account_data["country"]
        )
        accounts_db[account_id] = account
        created_accounts.append({
            "account_id": account_id,
            "account_type": account.account_type,
            "interest_rate": account.interest_rate,
            "bank_code": account.bank_code,
            "country": account.country,
            "account_name": account.account_name,
            "balance": account.balance,
            "currency": account.currency,
            "created_at": account.created_at
        })
    
    return created_accounts

@mcp.resource("accounts://{customer_id}")
def get_accounts(customer_id: str) -> List[Dict]:
    """Get all accounts for a customer"""
    return list(accounts_db.values())

@mcp.resource("account://{account_id}")
def get_account_details(account_id: str) -> Dict:
    """Get detailed information about a specific account"""
    account = accounts_db.get(account_id)
    if not account:
        return {"error": "Account not found"}
    return {
        "account_id": account.account_id,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "interest_rate": account.interest_rate,
        "bank_code": account.bank_code,
        "country": account.country,
        "balance": account.balance,
        "currency": account.currency,
        "created_at": account.created_at
    }

# Beneficiary Management
@mcp.tool()
def add_beneficiary(name: str, cust_account_id: str, ben_account_id: str, bank_code: str, currency: str, country: str) -> Dict:
    """Add a new beneficiary"""
    beneficiary_id = str(uuid4())
    beneficiaries_db[beneficiary_id] = {
        "beneficiary_id": beneficiary_id,
        "name": name,
        "cust_account_id": cust_account_id,
        "ben_account_id": ben_account_id,
        "bank_code": bank_code,
        "currency": currency,
        "country": country
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
    
    currency = beneficiaries_db.get(beneficiary_id)["currency"]
    if currency in blocked_currencies_db:
        return {"status": "error", "message": "Payment blocked for the currency: " + currency}
    
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
    account = accounts_db.get(account_id)
    if not account:
        return {"error": "Account not found"}
    return {
        "account_id": account.account_id,
        "account_name": account.account_name,
        "interest_rate": account.interest_rate,
        "bank_code": account.bank_code,
        "country": account.country,
        "balance": account.balance,
        "currency": account.currency,
        "last_updated": datetime.now().isoformat()
    }

    