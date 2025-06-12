from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class AccountType(enum.Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    INVESTMENT = "INVESTMENT"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"

class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(String(36), primary_key=True)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'account_id': self.account_id,
            'account_type': self.account_type.value,
            'balance': float(self.balance),
            'currency': self.currency,
            'created_at': self.created_at.isoformat()
        }

class Beneficiary(Base):
    __tablename__ = 'beneficiaries'

    beneficiary_id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_code = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payments = relationship("Payment", back_populates="beneficiary")

    def to_dict(self):
        return {
            'beneficiary_id': self.beneficiary_id,
            'name': self.name,
            'account_number': self.account_number,
            'bank_code': self.bank_code,
            'created_at': self.created_at.isoformat()
        }

class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(String(36), primary_key=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    beneficiary_id = Column(String(36), ForeignKey('beneficiaries.beneficiary_id'), nullable=False)
    status = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    beneficiary = relationship("Beneficiary", back_populates="payments")

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'beneficiary_id': self.beneficiary_id,
            'status': self.status,
            'type': self.type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 