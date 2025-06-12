# server.py
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum
from models import Account, Beneficiary, Payment, AccountType
from database import db
from sqlalchemy import or_, and_, desc, asc

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
    session = db.get_session()
    try:
        query = session.query(Account)
        
        if account_type:
            query = query.filter(Account.account_type == AccountType(account_type))
        
        if currency:
            query = query.filter(Account.currency == currency)
        
        if min_balance is not None:
            query = query.filter(Account.balance >= min_balance)
        
        if max_balance is not None:
            query = query.filter(Account.balance <= max_balance)
        
        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order_by(desc(getattr(Account, sort_by)))
        else:
            query = query.order_by(asc(getattr(Account, sort_by)))
        
        accounts = query.all()
        return [account.to_dict() for account in accounts]
    finally:
        db.close_session(session)

@mcp.tool()
def get_account_summary() -> Dict:
    """Get a summary of all accounts including total balance by currency and account type"""
    session = db.get_session()
    try:
        # Get total balance by currency
        balance_by_currency = {}
        for currency in session.query(Account.currency).distinct():
            total = session.query(Account).filter(Account.currency == currency[0]).with_entities(
                func.sum(Account.balance)).scalar() or 0
            balance_by_currency[currency[0]] = float(total)
        
        # Get count by account type
        accounts_by_type = {}
        for acc_type in AccountType:
            count = session.query(Account).filter(Account.account_type == acc_type).count()
            accounts_by_type[acc_type.value] = count
        
        total_accounts = sum(accounts_by_type.values())
        
        return {
            "total_accounts": total_accounts,
            "balance_by_currency": balance_by_currency,
            "accounts_by_type": accounts_by_type,
            "last_updated": datetime.now().isoformat()
        }
    finally:
        db.close_session(session)

@mcp.tool()
def add_account(account_type: str, balance: float, currency: str) -> Dict:
    """Add a single bank account"""
    session = db.get_session()
    try:
        account = Account(
            account_id=str(uuid4()),
            account_type=AccountType(account_type),
            balance=balance,
            currency=currency
        )
        session.add(account)
        session.commit()
        return account.to_dict()
    finally:
        db.close_session(session)

@mcp.tool()
def add_multiple_accounts(accounts: List[Dict]) -> List[Dict]:
    """Add multiple bank accounts at once"""
    session = db.get_session()
    try:
        new_accounts = []
        for account_data in accounts:
            account = Account(
                account_id=str(uuid4()),
                account_type=AccountType(account_data["account_type"]),
                balance=account_data["balance"],
                currency=account_data["currency"]
            )
            session.add(account)
            new_accounts.append(account)
        
        session.commit()
        return [account.to_dict() for account in new_accounts]
    finally:
        db.close_session(session)

@mcp.resource("accounts://{customer_id}")
def get_accounts(customer_id: str) -> List[Dict]:
    """Get all accounts for a customer"""
    session = db.get_session()
    try:
        accounts = session.query(Account).all()
        return [account.to_dict() for account in accounts]
    finally:
        db.close_session(session)

@mcp.resource("account://{account_id}")
def get_account_details(account_id: str) -> Dict:
    """Get detailed information about a specific account"""
    session = db.get_session()
    try:
        account = session.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            return {"error": "Account not found"}
        return account.to_dict()
    finally:
        db.close_session(session)

# Beneficiary Management
@mcp.tool()
def add_beneficiary(name: str, account_number: str, bank_code: str) -> Dict:
    """Add a new beneficiary"""
    session = db.get_session()
    try:
        beneficiary = Beneficiary(
            beneficiary_id=str(uuid4()),
            name=name,
            account_number=account_number,
            bank_code=bank_code
        )
        session.add(beneficiary)
        session.commit()
        return beneficiary.to_dict()
    finally:
        db.close_session(session)

@mcp.tool()
def delete_beneficiary(beneficiary_id: str) -> Dict:
    """Delete a beneficiary"""
    session = db.get_session()
    try:
        beneficiary = session.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if beneficiary:
            session.delete(beneficiary)
            session.commit()
            return {"status": "success", "message": "Beneficiary deleted successfully"}
        return {"status": "error", "message": "Beneficiary not found"}
    finally:
        db.close_session(session)

@mcp.resource("beneficiaries://{customer_id}")
def get_beneficiaries(customer_id: str) -> List[Dict]:
    """Get all beneficiaries for a customer"""
    session = db.get_session()
    try:
        beneficiaries = session.query(Beneficiary).all()
        return [beneficiary.to_dict() for beneficiary in beneficiaries]
    finally:
        db.close_session(session)

@mcp.tool()
def search_beneficiaries(name: Optional[str] = None, bank_code: Optional[str] = None) -> List[Dict]:
    """Search beneficiaries by name or bank code"""
    session = db.get_session()
    try:
        query = session.query(Beneficiary)
        
        if name:
            query = query.filter(Beneficiary.name.ilike(f"%{name}%"))
        
        if bank_code:
            query = query.filter(Beneficiary.bank_code == bank_code)
        
        beneficiaries = query.all()
        return [beneficiary.to_dict() for beneficiary in beneficiaries]
    finally:
        db.close_session(session)

# Payment Operations
@mcp.tool()
def initiate_payment(amount: float, currency: str, beneficiary_id: str) -> Dict:
    """Initiate an immediate payment"""
    session = db.get_session()
    try:
        # Check if beneficiary exists
        beneficiary = session.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if not beneficiary:
            return {"status": "error", "message": "Beneficiary not found"}
        
        payment = Payment(
            payment_id=str(uuid4()),
            amount=amount,
            currency=currency,
            beneficiary_id=beneficiary_id,
            status="PENDING",
            type="IMMEDIATE"
        )
        session.add(payment)
        session.commit()
        return payment.to_dict()
    finally:
        db.close_session(session)

@mcp.tool()
def schedule_payment(amount: float, currency: str, beneficiary_id: str, 
                    scheduled_date: datetime) -> Dict:
    """Schedule a future payment"""
    session = db.get_session()
    try:
        # Check if beneficiary exists
        beneficiary = session.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if not beneficiary:
            return {"status": "error", "message": "Beneficiary not found"}
        
        payment = Payment(
            payment_id=str(uuid4()),
            amount=amount,
            currency=currency,
            beneficiary_id=beneficiary_id,
            status="SCHEDULED",
            type="SCHEDULED",
            scheduled_date=scheduled_date
        )
        session.add(payment)
        session.commit()
        return payment.to_dict()
    finally:
        db.close_session(session)

@mcp.tool()
def cancel_payment(payment_id: str) -> Dict:
    """Cancel a scheduled payment"""
    session = db.get_session()
    try:
        payment = session.query(Payment).filter(
            Payment.payment_id == payment_id,
            Payment.status == "SCHEDULED"
        ).first()
        
        if payment:
            payment.status = "CANCELLED"
            session.commit()
            return {
                "payment_id": payment_id,
                "status": "CANCELLED",
                "message": "Payment cancelled successfully"
            }
        return {"status": "error", "message": "Payment not found or cannot be cancelled"}
    finally:
        db.close_session(session)

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
    session = db.get_session()
    try:
        query = session.query(Payment)
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        if min_amount is not None:
            query = query.filter(Payment.amount >= min_amount)
        
        if max_amount is not None:
            query = query.filter(Payment.amount <= max_amount)
        
        if currency:
            query = query.filter(Payment.currency == currency)
        
        if status:
            query = query.filter(Payment.status == status)
        
        if payment_type:
            query = query.filter(Payment.type == payment_type)
        
        if beneficiary_id:
            query = query.filter(Payment.beneficiary_id == beneficiary_id)
        
        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order_by(desc(getattr(Payment, sort_by)))
        else:
            query = query.order_by(asc(getattr(Payment, sort_by)))
        
        if limit is not None:
            query = query.limit(limit)
        
        payments = query.all()
        return [payment.to_dict() for payment in payments]
    finally:
        db.close_session(session)

@mcp.tool()
def get_payment_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """Get payment statistics for a given date range"""
    session = db.get_session()
    try:
        query = session.query(Payment)
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        # Get total payments and amount
        total_payments = query.count()
        total_amount = query.with_entities(func.sum(Payment.amount)).scalar() or 0
        
        # Get status breakdown
        status_counts = {}
        for status in query.with_entities(Payment.status).distinct():
            count = query.filter(Payment.status == status[0]).count()
            status_counts[status[0]] = count
        
        # Get currency breakdown
        currency_amounts = {}
        for currency in query.with_entities(Payment.currency).distinct():
            amount = query.filter(Payment.currency == currency[0]).with_entities(
                func.sum(Payment.amount)).scalar() or 0
            currency_amounts[currency[0]] = float(amount)
        
        # Get type breakdown
        type_counts = {}
        for payment_type in query.with_entities(Payment.type).distinct():
            count = query.filter(Payment.type == payment_type[0]).count()
            type_counts[payment_type[0]] = count
        
        return {
            "total_payments": total_payments,
            "total_amount": float(total_amount),
            "status_breakdown": status_counts,
            "currency_breakdown": currency_amounts,
            "type_breakdown": type_counts,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "last_updated": datetime.now().isoformat()
        }
    finally:
        db.close_session(session)

@mcp.resource("payments://{customer_id}")
def get_payments(customer_id: str) -> List[Dict]:
    """Get all payments for a customer"""
    session = db.get_session()
    try:
        payments = session.query(Payment).all()
        return [payment.to_dict() for payment in payments]
    finally:
        db.close_session(session)

# Balance Check
@mcp.resource("balance://{account_id}")
def get_account_balance(account_id: str) -> Dict:
    """Get current balance for an account"""
    session = db.get_session()
    try:
        account = session.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            return {"error": "Account not found"}
        
        return {
            "account_id": account.account_id,
            "balance": float(account.balance),
            "currency": account.currency,
            "last_updated": datetime.now().isoformat()
        }
    finally:
        db.close_session(session) 