from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import Booking, BookingCreate
from app.services import BookingService
from app.api.auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=Booking)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return BookingService.create_booking(db, booking, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Booking failed. Please try again."
        )

@router.get("/", response_model=List[Booking])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return BookingService.get_user_bookings(db, current_user.id)

@router.get("/{booking_id}", response_model=Booking)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    booking = BookingService.get_booking_by_id(db, booking_id, current_user.id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking

@router.put("/{booking_id}")
def update_booking(
    booking_id: int,
    passengers: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        BookingService.update_booking_passengers(db, booking_id, current_user.id, passengers['passengers'])
        return {"message": "Booking updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{booking_id}/cancel")
def cancel_booking_with_refund(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        refund_amount = BookingService.cancel_booking_with_refund(db, booking_id, current_user.id)
        return {"message": "Booking cancelled and refunded successfully", "refund_amount": refund_amount}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))