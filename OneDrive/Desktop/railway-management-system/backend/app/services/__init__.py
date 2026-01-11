from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from app.models import User, Station, Train, Route, TrainSchedule, Booking, Passenger
from app.schemas import UserCreate, StationCreate, TrainCreate, RouteCreate, BookingCreate, TrainSearchRequest
from app.core.security import get_password_hash, verify_password
from datetime import datetime, timedelta
from typing import List, Optional
import random
import string

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
            full_name=user.full_name,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return False
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

class StationService:
    @staticmethod
    def create_station(db: Session, station: StationCreate):
        db_station = Station(**station.dict())
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
        return db_station
    
    @staticmethod
    def get_all_stations(db: Session):
        return db.query(Station).all()
    
    @staticmethod
    def get_station_by_id(db: Session, station_id: int):
        return db.query(Station).filter(Station.id == station_id).first()

class TrainService:
    @staticmethod
    def create_train(db: Session, train: TrainCreate):
        # Check if train number already exists
        existing_train = db.query(Train).filter(Train.number == train.number).first()
        if existing_train:
            raise ValueError(f"Train number {train.number} already exists")
        
        db_train = Train(**train.dict())
        db.add(db_train)
        db.commit()
        db.refresh(db_train)
        return db_train
    
    @staticmethod
    def get_all_trains(db: Session):
        return db.query(Train).all()  # Return all trains including inactive ones
    
    @staticmethod
    def get_train(db: Session, train_id: int):
        return db.query(Train).filter(Train.id == train_id).first()
    
    @staticmethod
    def update_train(db: Session, train_id: int, train_data: TrainCreate):
        db_train = db.query(Train).filter(Train.id == train_id).first()
        if not db_train:
            return None
        for key, value in train_data.dict().items():
            setattr(db_train, key, value)
        db.commit()
        db.refresh(db_train)
        return db_train
    
    @staticmethod
    def toggle_train_status(db: Session, train_id: int):
        db_train = db.query(Train).filter(Train.id == train_id).first()
        if not db_train:
            return None
        
        # Toggle train status
        db_train.is_active = not db_train.is_active
        
        # Also toggle all routes associated with this train
        db.query(Route).filter(Route.train_id == train_id).update(
            {Route.is_active: db_train.is_active}
        )
        
        db.commit()
        db.refresh(db_train)
        
        status = "activated" if db_train.is_active else "deactivated"
        return {"message": f"Train and its routes {status} successfully", "is_active": db_train.is_active}
    
    @staticmethod
    def sync_routes_with_trains(db: Session):
        """Sync all routes status with their associated trains"""
        # Update all routes to match their train's active status
        db.execute(
            text("UPDATE routes SET is_active = (SELECT is_active FROM trains WHERE trains.id = routes.train_id)")
        )
        db.commit()
        return {"message": "All routes synced with their train status"}
    
    @staticmethod
    def delete_train(db: Session, train_id: int):
        db_train = db.query(Train).filter(Train.id == train_id).first()
        if not db_train:
            return None
        # Hard delete - permanently remove from database
        db.delete(db_train)
        db.commit()
        return {"message": "Train deleted successfully"}
    
    @staticmethod
    def get_admin_dashboard(db: Session):
        total_trains = db.query(Train).filter(Train.is_active == True).count()
        total_bookings = db.query(Booking).count()
        total_revenue = db.query(Booking).filter(Booking.status == 'confirmed').with_entities(func.sum(Booking.total_amount)).scalar() or 0
        active_users = db.query(User).filter(User.is_active == True).count()
        
        recent_bookings = db.query(Booking).order_by(Booking.booking_date.desc()).limit(10).all()
        
        return {
            "total_trains": total_trains,
            "total_bookings": total_bookings,
            "total_revenue": float(total_revenue),
            "active_users": active_users,
            "recent_bookings": recent_bookings
        }
    
    @staticmethod
    def search_trains(db: Session, search_request: TrainSearchRequest):
        return db.query(TrainSchedule).join(Route).join(Train).filter(
            and_(
                Route.source_station_id == search_request.source_station_id,
                Route.destination_station_id == search_request.destination_station_id,
                TrainSchedule.schedule_date == search_request.travel_date,
                TrainSchedule.available_seats > 0,
                Route.is_active == True,
                Train.is_active == True
            )
        ).all()

class RouteService:
    @staticmethod
    def create_route(db: Session, route: RouteCreate):
        # Validate source and destination are different
        if route.source_station_id == route.destination_station_id:
            raise ValueError("Source and destination stations cannot be the same")
        
        # Check if route already exists for the same train and stations
        existing_route = db.query(Route).filter(
            Route.train_id == route.train_id,
            Route.source_station_id == route.source_station_id,
            Route.destination_station_id == route.destination_station_id,
            Route.is_active == True
        ).first()
        if existing_route:
            raise ValueError("Route already exists for this train and stations")
        
        db_route = Route(**route.dict())
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        
        # Auto-create train schedules for the next 30 days
        RouteService.create_schedules_for_route(db, db_route.id)
        
        return db_route
    
    @staticmethod
    def create_schedules_for_route(db: Session, route_id: int, days_ahead: int = 30):
        """Create train schedules for a route for the next N days"""
        from datetime import date, timedelta
        
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return
        
        today = date.today()
        
        for i in range(days_ahead):
            schedule_date = today + timedelta(days=i)
            
            # Check if schedule already exists
            existing_schedule = db.query(TrainSchedule).filter(
                TrainSchedule.route_id == route_id,
                TrainSchedule.schedule_date == schedule_date
            ).first()
            
            if not existing_schedule:
                schedule = TrainSchedule(
                    route_id=route_id,
                    schedule_date=schedule_date,
                    available_seats=route.train.total_seats
                )
                db.add(schedule)
        
        db.commit()
    
    @staticmethod
    def get_all_routes(db: Session):
        return db.query(Route).filter(Route.is_active == True).all()
    
    @staticmethod
    def get_route(db: Session, route_id: int):
        return db.query(Route).filter(Route.id == route_id).first()
    
    @staticmethod
    def update_route(db: Session, route_id: int, route_data: RouteCreate):
        db_route = db.query(Route).filter(Route.id == route_id).first()
        if not db_route:
            return None
        for key, value in route_data.dict().items():
            setattr(db_route, key, value)
        db.commit()
        db.refresh(db_route)
        return db_route
    
    @staticmethod
    def delete_route(db: Session, route_id: int):
        db_route = db.query(Route).filter(Route.id == route_id).first()
        if not db_route:
            return None
        # Hard delete - permanently remove from database
        db.delete(db_route)
        db.commit()
        return {"message": "Route deleted successfully"}

class BookingService:
    @staticmethod
    def generate_booking_reference():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @staticmethod
    def create_booking(db: Session, booking: BookingCreate, user_id: int):
        from datetime import timedelta
        # Check seat availability
        schedule = db.query(TrainSchedule).filter(TrainSchedule.id == booking.schedule_id).first()
        if not schedule or schedule.available_seats < len(booking.passengers):
            raise ValueError("Insufficient seats available")
        
        # Calculate total amount
        total_amount = schedule.route.base_fare * len(booking.passengers)
        
        # Calculate journey dates
        journey_date_from = schedule.schedule_date
        # Assume 1 day per 500km, minimum 1 day
        days = max(1, (schedule.route.distance_km + 499) // 500)  # Ceiling division
        journey_date_to = journey_date_from + timedelta(days=days - 1)
        
        # Create booking
        db_booking = Booking(
            user_id=user_id,
            schedule_id=booking.schedule_id,
            booking_reference=BookingService.generate_booking_reference(),
            passenger_count=len(booking.passengers),
            total_amount=total_amount,
            journey_date_from=journey_date_from,
            journey_date_to=journey_date_to
        )
        db.add(db_booking)
        db.flush()  # Get booking ID
        
        # Add passengers
        for passenger_data in booking.passengers:
            passenger = Passenger(
                booking_id=db_booking.id,
                name=passenger_data.name,
                age=passenger_data.age,
                gender=passenger_data.gender
            )
            db.add(passenger)
        
        # Update available seats
        schedule.available_seats -= len(booking.passengers)
        
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    @staticmethod
    def get_user_bookings(db: Session, user_id: int):
        return db.query(Booking).filter(Booking.user_id == user_id).all()
    
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int, user_id: int):
        return db.query(Booking).filter(
            and_(Booking.id == booking_id, Booking.user_id == user_id)
        ).first()
    
    @staticmethod
    def update_booking_passengers(db: Session, booking_id: int, user_id: int, passengers_data: list):
        booking = db.query(Booking).filter(
            and_(Booking.id == booking_id, Booking.user_id == user_id)
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != "confirmed":
            raise ValueError("Only confirmed bookings can be edited")
        
        # Update passenger details
        for i, passenger_data in enumerate(passengers_data):
            if i < len(booking.passengers):
                passenger = booking.passengers[i]
                passenger.name = passenger_data['name']
                passenger.age = passenger_data['age']
                passenger.gender = passenger_data['gender']
        
        db.commit()
        return booking
    
    @staticmethod
    def cancel_booking_with_refund(db: Session, booking_id: int, user_id: int):
        from app.models import RefundRequest
        
        booking = db.query(Booking).filter(
            and_(Booking.id == booking_id, Booking.user_id == user_id)
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != "confirmed":
            raise ValueError("Only confirmed bookings can be cancelled")
        
        # Cancel booking
        booking.status = "cancelled"
        
        # Restore seats
        schedule = db.query(TrainSchedule).filter(TrainSchedule.id == booking.schedule_id).first()
        schedule.available_seats += booking.passenger_count
        
        # Create refund request instead of immediate refund
        refund_request = RefundRequest(
            booking_id=booking_id,
            user_id=user_id,
            amount=booking.total_amount
        )
        db.add(refund_request)
        
        db.commit()
        
        return {"message": "Booking cancelled. Refund request submitted for admin approval.", "refund_amount": float(booking.total_amount)}

class RefundService:
    @staticmethod
    def get_pending_refund_requests(db: Session):
        from app.models import RefundRequest
        return db.query(RefundRequest).filter(RefundRequest.status == "pending").all()
    
    @staticmethod
    def approve_refund_request(db: Session, request_id: int, admin_id: int):
        from app.models import RefundRequest, SystemAlert, AlertType
        from datetime import datetime
        
        refund_request = db.query(RefundRequest).filter(RefundRequest.id == request_id).first()
        if not refund_request:
            raise ValueError("Refund request not found")
        
        if refund_request.status != "pending":
            raise ValueError("Refund request is not pending")
        
        # Update refund request
        refund_request.status = "approved"
        refund_request.approved_at = datetime.utcnow()
        refund_request.admin_id = admin_id
        
        # Note: Wallet functionality not implemented yet
        # For now, just mark as approved and create alert
        
        # Create system alert for refund approval
        alert = SystemAlert(
            alert_type=AlertType.success,
            title="Refund Approved",
            message=f"Refund of ₹{refund_request.amount} approved for booking {refund_request.booking.booking_reference}",
            icon="check-circle",
            dismissible=True
        )
        db.add(alert)
        
        db.commit()
        
        return refund_request
    
    @staticmethod
    def reject_refund_request(db: Session, request_id: int, admin_id: int, reason: str = None):
        from app.models import RefundRequest
        from datetime import datetime
        
        refund_request = db.query(RefundRequest).filter(RefundRequest.id == request_id).first()
        if not refund_request:
            raise ValueError("Refund request not found")
        
        if refund_request.status != "pending":
            raise ValueError("Refund request is not pending")
        
        # Update refund request
        refund_request.status = "rejected"
        refund_request.approved_at = datetime.utcnow()
        refund_request.admin_id = admin_id
        refund_request.rejection_reason = reason
        
        # Create system alert for refund rejection
        from app.models import SystemAlert, AlertType
        alert = SystemAlert(
            alert_type=AlertType.warning,
            title="Refund Rejected",
            message=f"Refund request for booking {refund_request.booking.booking_reference} was rejected{f': {reason}' if reason else ''}",
            icon="times-circle",
            dismissible=True
        )
        db.add(alert)
        
        db.commit()
        
        return refund_request