from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    WALLET = "WALLET"
    UPI = "UPI"

class PaymentStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

# Credit Card Schemas
class CreditCardCreate(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19)
    cardholder_name: str = Field(..., min_length=1, max_length=100)
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2024, le=2050)
    cvv: str = Field(..., min_length=3, max_length=4)
    card_type: str = Field(..., min_length=1, max_length=20)

class CreditCard(BaseModel):
    id: int
    card_number: str  # Masked
    cardholder_name: str
    expiry_month: int
    expiry_year: int
    card_type: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CardTransaction(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# UPI Schemas
class UpiIdCreate(BaseModel):
    upi_id: str = Field(..., min_length=1, max_length=100)

class UpiId(BaseModel):
    id: int
    upi_id: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UpiTransaction(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Wallet Schemas
class WalletAddMoney(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)

class WalletTransaction(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Wallet(BaseModel):
    id: int
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Payment Schemas
class PaymentCreate(BaseModel):
    booking_id: int
    payment_method: PaymentMethodEnum
    card_id: Optional[int] = None  # For card payments
    upi_id: Optional[int] = None   # For UPI payments

class Payment(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    payment_method: PaymentMethodEnum
    status: PaymentStatusEnum
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)