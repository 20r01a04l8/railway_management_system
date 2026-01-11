from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.booking import Booking, Passenger
from app.models.train import TrainSchedule
from app.schemas.booking import BookingCreate, BookingUpdate
from app.core.exceptions import InsufficientSeatsError, NotFoundError
import logging

logger = logging.getLogger(__name__)


class BookingRepository(BaseRepository[Booking, BookingCreate, BookingUpdate]):
    """Repository for booking operations with seat locking."""
    
    def __init__(self):
        super().__init__(Booking)
    
    async def create_booking_with_seat_lock(
        self,
        db: AsyncSession,
        *,
        booking_data: BookingCreate,
        user_id: int
    ) -> Booking:
        """Create booking with pessimistic seat locking."""
        
        # Start transaction with row-level locking
        async with db.begin():
            # Lock the train schedule row for update
            schedule_query = (
                select(TrainSchedule)
                .where(TrainSchedule.id == booking_data.schedule_id)
                .with_for_update()  # Pessimistic lock
            )
            
            result = await db.execute(schedule_query)
            schedule = result.scalar_one_or_none()
            
            if not schedule:
                raise NotFoundError("TrainSchedule", booking_data.schedule_id)
            
            passenger_count = len(booking_data.passengers)
            
            # Check seat availability under lock
            if schedule.available_seats < passenger_count:
                raise InsufficientSeatsError(
                    available=schedule.available_seats,
                    requested=passenger_count
                )
            
            # Calculate total amount
            total_amount = schedule.route.base_fare * passenger_count
            
            # Create booking
            booking = Booking(
                user_id=user_id,
                schedule_id=booking_data.schedule_id,
                booking_reference=self._generate_booking_reference(),
                passenger_count=passenger_count,
                total_amount=total_amount,
                status="confirmed"
            )
            
            db.add(booking)
            await db.flush()  # Get booking ID without committing
            
            # Create passengers
            for passenger_data in booking_data.passengers:
                passenger = Passenger(
                    booking_id=booking.id,
                    name=passenger_data.name,
                    age=passenger_data.age,
                    gender=passenger_data.gender
                )
                db.add(passenger)
            
            # Update available seats
            schedule.available_seats -= passenger_count
            
            # Log the booking operation
            logger.info(
                f"Booking created: {booking.booking_reference}",
                extra={
                    "booking_id": booking.id,
                    "user_id": user_id,
                    "schedule_id": booking_data.schedule_id,
                    "passenger_count": passenger_count,
                    "seats_remaining": schedule.available_seats
                }
            )
            
            await db.commit()
            await db.refresh(booking)
            
            return booking
    
    async def cancel_booking_with_seat_release(
        self,
        db: AsyncSession,
        *,
        booking_id: int,
        user_id: int
    ) -> Optional[Booking]:
        """Cancel booking and release seats."""
        
        async with db.begin():
            # Get booking with lock
            booking_query = (
                select(Booking)
                .options(selectinload(Booking.schedule))
                .where(
                    and_(
                        Booking.id == booking_id,
                        Booking.user_id == user_id,
                        Booking.status == "confirmed"
                    )
                )
                .with_for_update()
            )
            
            result = await db.execute(booking_query)
            booking = result.scalar_one_or_none()
            
            if not booking:
                return None
            
            # Lock the schedule for update
            schedule_query = (
                select(TrainSchedule)
                .where(TrainSchedule.id == booking.schedule_id)
                .with_for_update()
            )
            
            result = await db.execute(schedule_query)
            schedule = result.scalar_one()
            
            # Update booking status
            booking.status = "cancelled"
            
            # Release seats
            schedule.available_seats += booking.passenger_count
            
            logger.info(
                f"Booking cancelled: {booking.booking_reference}",
                extra={
                    "booking_id": booking.id,
                    "user_id": user_id,
                    "seats_released": booking.passenger_count,
                    "seats_available": schedule.available_seats
                }
            )
            
            await db.commit()
            await db.refresh(booking)
            
            return booking
    
    async def get_user_bookings(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Booking]:
        """Get user bookings with related data."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.schedule).selectinload(TrainSchedule.route),
                selectinload(Booking.passengers)
            )
            .where(Booking.user_id == user_id)
            .order_by(Booking.booking_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_booking_by_reference(
        self,
        db: AsyncSession,
        *,
        booking_reference: str
    ) -> Optional[Booking]:
        """Get booking by reference number."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.schedule).selectinload(TrainSchedule.route),
                selectinload(Booking.passengers),
                selectinload(Booking.user)
            )
            .where(Booking.booking_reference == booking_reference)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_revenue_stats(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> dict:
        """Get revenue statistics."""
        query = select(
            func.count(Booking.id).label("total_bookings"),
            func.sum(Booking.total_amount).label("total_revenue"),
            func.sum(Booking.passenger_count).label("total_passengers")
        ).where(Booking.status == "confirmed")
        
        if start_date:
            query = query.where(Booking.booking_date >= start_date)
        if end_date:
            query = query.where(Booking.booking_date <= end_date)
        
        result = await db.execute(query)
        stats = result.first()
        
        return {
            "total_bookings": stats.total_bookings or 0,
            "total_revenue": float(stats.total_revenue or 0),
            "total_passengers": stats.total_passengers or 0
        }
    
    def _generate_booking_reference(self) -> str:
        """Generate unique booking reference."""
        import secrets
        import string
        return ''.join(secrets.choices(string.ascii_uppercase + string.digits, k=8))


# Repository instance
booking_repository = BookingRepository()