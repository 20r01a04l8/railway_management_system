from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.models.payment import CreditCard, Wallet, WalletTransaction, Payment, PaymentStatus, PaymentMethod, UpiId, CardTransaction, UpiTransaction
from app.models import User, Booking
from app.schemas.payment import (
    CreditCardCreate, CreditCard as CreditCardSchema, CardTransaction as CardTransactionSchema,
    UpiIdCreate, UpiId as UpiIdSchema, UpiTransaction as UpiTransactionSchema,
    WalletAddMoney, Wallet as WalletSchema, WalletTransaction as WalletTransactionSchema, 
    PaymentCreate, Payment as PaymentSchema
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

# Credit Card endpoints
@router.post("/credit-cards", response_model=CreditCardSchema)
def add_credit_card(
    card_data: CreditCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate card number is exactly 16 digits
    if len(card_data.card_number) != 16 or not card_data.card_number.isdigit():
        raise HTTPException(status_code=400, detail="Card number must be exactly 16 digits")
    
    # Validate CVV is exactly 3 digits
    if len(card_data.cvv) != 3 or not card_data.cvv.isdigit():
        raise HTTPException(status_code=400, detail="CVV must be exactly 3 digits")
    
    # Mask card number for storage (in production, use proper encryption)
    masked_number = "**** **** **** " + card_data.card_number[-4:]
    
    credit_card = CreditCard(
        user_id=current_user.id,
        card_number=masked_number,
        cardholder_name=card_data.cardholder_name,
        expiry_month=card_data.expiry_month,
        expiry_year=card_data.expiry_year,
        cvv="***",  # Never store actual CVV
        card_type=card_data.card_type,
        balance=Decimal('10000.00')  # Default balance
    )
    
    db.add(credit_card)
    db.commit()
    db.refresh(credit_card)
    return credit_card

@router.get("/credit-cards", response_model=List[CreditCardSchema])
def get_credit_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(CreditCard).filter(CreditCard.user_id == current_user.id, CreditCard.is_active == True).all()

@router.delete("/credit-cards/{card_id}")
def delete_credit_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(CreditCard).filter(CreditCard.id == card_id, CreditCard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    card.is_active = False
    db.commit()
    return {"message": "Credit card deleted successfully"}

@router.get("/credit-cards/{card_id}/transactions", response_model=List[CardTransactionSchema])
def get_card_transactions(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(CreditCard).filter(CreditCard.id == card_id, CreditCard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    return db.query(CardTransaction).filter(CardTransaction.card_id == card_id).order_by(CardTransaction.created_at.desc()).all()

# Wallet endpoints
@router.get("/wallet", response_model=WalletSchema)
def get_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        # Create wallet if doesn't exist
        wallet = Wallet(user_id=current_user.id, balance=Decimal('0.00'))
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@router.post("/wallet/add-money")
def add_money_to_wallet(
    money_data: WalletAddMoney,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=current_user.id, balance=Decimal('0.00'))
        db.add(wallet)
        db.flush()
    
    # Add money to wallet
    wallet.balance += money_data.amount
    
    # Create transaction record
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type="credit",
        amount=money_data.amount,
        description="Money added to wallet",
        reference_id=str(uuid.uuid4())
    )
    
    db.add(transaction)
    db.commit()
    
    return {"message": "Money added successfully", "new_balance": wallet.balance}

@router.get("/wallet/transactions", response_model=List[WalletTransactionSchema])
def get_wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        return []
    
    return db.query(WalletTransaction).filter(WalletTransaction.wallet_id == wallet.id).order_by(WalletTransaction.created_at.desc()).all()

# UPI ID endpoints (must come before generic payment endpoints)
@router.post("/upi-ids", response_model=UpiIdSchema)
def add_upi_id(
    upi_data: UpiIdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate UPI ID format (basic validation)
    if '@' not in upi_data.upi_id:
        raise HTTPException(status_code=400, detail="Invalid UPI ID format")
    
    upi_id = UpiId(
        user_id=current_user.id,
        upi_id=upi_data.upi_id,
        balance=Decimal('10000.00')  # Default balance
    )
    
    db.add(upi_id)
    db.commit()
    db.refresh(upi_id)
    return upi_id

@router.get("/upi-ids", response_model=List[UpiIdSchema])
def get_upi_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UpiId).filter(UpiId.user_id == current_user.id, UpiId.is_active == True).all()

@router.delete("/upi-ids/{upi_id}")
def delete_upi_id(
    upi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upi = db.query(UpiId).filter(UpiId.id == upi_id, UpiId.user_id == current_user.id).first()
    if not upi:
        raise HTTPException(status_code=404, detail="UPI ID not found")
    
    upi.is_active = False
    db.commit()
    return {"message": "UPI ID deleted successfully"}

@router.get("/upi-ids/{upi_id}/transactions", response_model=List[UpiTransactionSchema])
def get_upi_transactions(
    upi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upi = db.query(UpiId).filter(UpiId.id == upi_id, UpiId.user_id == current_user.id).first()
    if not upi:
        raise HTTPException(status_code=404, detail="UPI ID not found")
    
    return db.query(UpiTransaction).filter(UpiTransaction.upi_id == upi_id).order_by(UpiTransaction.created_at.desc()).all()

@router.post("/upi-ids/{upi_id}/deduct")
def deduct_from_upi(
    upi_id: int,
    deduct_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upi = db.query(UpiId).filter(UpiId.id == upi_id, UpiId.user_id == current_user.id).first()
    if not upi:
        raise HTTPException(status_code=404, detail="UPI ID not found")
    
    amount = Decimal(str(deduct_data['amount']))
    if upi.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    upi.balance -= amount
    
    transaction = UpiTransaction(
        upi_id=upi.id,
        transaction_type="debit",
        amount=amount,
        description=deduct_data.get('description', 'Payment'),
        reference_id=str(uuid.uuid4())
    )
    
    db.add(transaction)
    db.commit()
    
    return {"message": "Amount deducted successfully", "new_balance": upi.balance}

# Payment endpoints (must come after specific endpoints)
@router.post("/process", response_model=PaymentSchema)
def process_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get booking
    booking = db.query(Booking).filter(Booking.id == payment_data.booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if payment already exists
    existing_payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already processed for this booking")
    
    # Process payment based on method
    if payment_data.payment_method == PaymentMethod.WALLET:
        wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
        if not wallet or wallet.balance < booking.total_amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Deduct from wallet
        wallet.balance -= booking.total_amount
        
        # Create wallet transaction
        wallet_transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type="debit",
            amount=booking.total_amount,
            description=f"Payment for booking {booking.booking_reference}",
            reference_id=str(booking.id)
        )
        db.add(wallet_transaction)
    
    elif payment_data.payment_method == PaymentMethod.CREDIT_CARD:
        if not payment_data.card_id:
            raise HTTPException(status_code=400, detail="Card ID required for credit card payment")
        
        card = db.query(CreditCard).filter(CreditCard.id == payment_data.card_id, CreditCard.user_id == current_user.id).first()
        if not card or not card.is_active:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        if card.balance < booking.total_amount:
            raise HTTPException(status_code=400, detail="Insufficient card balance")
        
        # Deduct from card
        card.balance -= booking.total_amount
        
        # Create card transaction
        card_transaction = CardTransaction(
            card_id=card.id,
            transaction_type="debit",
            amount=booking.total_amount,
            description=f"Payment for booking {booking.booking_reference}",
            reference_id=str(booking.id)
        )
        db.add(card_transaction)
    
    elif payment_data.payment_method == PaymentMethod.UPI:
        if not payment_data.upi_id:
            raise HTTPException(status_code=400, detail="UPI ID required for UPI payment")
        
        upi = db.query(UpiId).filter(UpiId.id == payment_data.upi_id, UpiId.user_id == current_user.id).first()
        if not upi or not upi.is_active:
            raise HTTPException(status_code=404, detail="UPI ID not found")
        
        if upi.balance < booking.total_amount:
            raise HTTPException(status_code=400, detail="Insufficient UPI balance")
        
        # Deduct from UPI
        upi.balance -= booking.total_amount
        
        # Create UPI transaction
        upi_transaction = UpiTransaction(
            upi_id=upi.id,
            transaction_type="debit",
            amount=booking.total_amount,
            description=f"Payment for booking {booking.booking_reference}",
            reference_id=str(booking.id)
        )
        db.add(upi_transaction)
    
    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        user_id=current_user.id,
        amount=booking.total_amount,
        payment_method=payment_data.payment_method,
        status=PaymentStatus.completed,
        transaction_id=str(uuid.uuid4())
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.get("/", response_model=List[PaymentSchema])
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).all()

@router.get("/{payment_id}", response_model=PaymentSchema)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/credit-cards/{card_id}/deduct")
def deduct_from_card(
    card_id: int,
    deduct_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(CreditCard).filter(CreditCard.id == card_id, CreditCard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    amount = Decimal(str(deduct_data['amount']))
    if card.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    card.balance -= amount
    
    transaction = CardTransaction(
        card_id=card.id,
        transaction_type="debit",
        amount=amount,
        description=deduct_data.get('description', 'Payment'),
        reference_id=str(uuid.uuid4())
    )
    
    db.add(transaction)
    db.commit()
    
    return {"message": "Amount deducted successfully", "new_balance": card.balance}