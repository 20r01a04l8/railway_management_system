from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Enum, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    WALLET = "WALLET"
    UPI = "UPI"

class CreditCard(Base):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String(19), nullable=False)  # Encrypted
    cardholder_name = Column(String(100), nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    cvv = Column(String(4), nullable=False)  # Encrypted
    card_type = Column(String(20), nullable=False)  # Visa, MasterCard, etc.
    balance = Column(DECIMAL(10, 2), nullable=False, default=10000.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="credit_cards")
    transactions = relationship("CardTransaction", back_populates="card")

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # credit, debit
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255))
    reference_id = Column(String(100))  # Payment ID or booking ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    wallet = relationship("Wallet", back_populates="transactions")

class UpiId(Base):
    __tablename__ = "upi_ids"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upi_id = Column(String(100), nullable=False)
    balance = Column(DECIMAL(10, 2), nullable=False, default=10000.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="upi_ids")
    transactions = relationship("UpiTransaction", back_populates="upi")

class CardTransaction(Base):
    __tablename__ = "card_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # credit, debit
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255))
    reference_id = Column(String(100))  # Payment ID or booking ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    card = relationship("CreditCard", back_populates="transactions")

class UpiTransaction(Base):
    __tablename__ = "upi_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    upi_id = Column(Integer, ForeignKey("upi_ids.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # credit, debit
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255))
    reference_id = Column(String(100))  # Payment ID or booking ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    upi = relationship("UpiId", back_populates="transactions")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    transaction_id = Column(String(100), unique=True)
    gateway_response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="payment")
    user = relationship("User", back_populates="payments")