from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Enum, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class TrainType(str, enum.Enum):
    express = "express"
    passenger = "passenger"
    superfast = "superfast"

class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class ScheduleStatus(str, enum.Enum):
    scheduled = "scheduled"
    running = "running"
    completed = "completed"
    cancelled = "cancelled"

class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class AlertType(str, enum.Enum):
    info = "info"
    warning = "warning"
    danger = "danger"
    success = "success"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    bookings = relationship("Booking", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    credit_cards = relationship("CreditCard", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    upi_ids = relationship("UpiId", back_populates="user")
    upi_ids = relationship("UpiId", back_populates="user")

class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(TrainType), nullable=False)
    total_seats = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    routes = relationship("Route", back_populates="train")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    source_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    distance_km = Column(Integer, nullable=False)
    base_fare = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    train = relationship("Train", back_populates="routes")
    source_station = relationship("Station", foreign_keys=[source_station_id])
    destination_station = relationship("Station", foreign_keys=[destination_station_id])
    schedules = relationship("TrainSchedule", back_populates="route")

class TrainSchedule(Base):
    __tablename__ = "train_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    schedule_date = Column(Date, nullable=False)
    available_seats = Column(Integer, nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.scheduled)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    route = relationship("Route", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("train_schedules.id"), nullable=False)
    booking_reference = Column(String(20), unique=True, nullable=False)
    passenger_count = Column(Integer, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.confirmed)
    booking_date = Column(DateTime(timezone=True), server_default=func.now())
    journey_date_from = Column(Date, nullable=False)
    journey_date_to = Column(Date, nullable=False)    
    user = relationship("User", back_populates="bookings")
    schedule = relationship("TrainSchedule", back_populates="bookings")
    passengers = relationship("Passenger", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False)

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    seat_number = Column(String(10))
    
    booking = relationship("Booking", back_populates="passengers")

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    icon = Column(String(50), default="info-circle")
    dismissible = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RefundRequest(Base):
    __tablename__ = "refund_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(RefundStatus, values_callable=lambda x: [e.value for e in x]), default=RefundStatus.PENDING)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    booking = relationship("Booking")
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())