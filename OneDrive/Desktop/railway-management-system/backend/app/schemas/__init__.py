from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
import re

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class TrainType(str, Enum):
    express = "express"
    passenger = "passenger"
    superfast = "superfast"

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and (len(v) != 10 or not v.isdigit()):
            raise ValueError('Phone number must be exactly 10 digits')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check password strength
        strength = get_password_strength(v)
        if strength == 'weak':
            raise ValueError('Password is too weak. Use a mix of uppercase, lowercase, numbers, and symbols')
        
        return v

def get_password_strength(password: str) -> str:
    """Calculate password strength"""
    score = 0
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 2:
        return 'weak'
    elif score <= 4:
        return 'medium'
    else:
        return 'strong'

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Station schemas
class StationBase(BaseModel):
    code: str
    name: str
    city: str
    state: str

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Train schemas
class TrainBase(BaseModel):
    number: str
    name: str
    type: TrainType
    total_seats: int

class TrainCreate(TrainBase):
    pass

class Train(TrainBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Route schemas
class RouteBase(BaseModel):
    train_id: int
    source_station_id: int
    destination_station_id: int
    departure_time: time
    arrival_time: time
    distance_km: int
    base_fare: Decimal

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: int
    is_active: bool
    created_at: datetime
    train: Train
    source_station: Station
    destination_station: Station
    
    model_config = ConfigDict(from_attributes=True)

# Search schemas
class TrainSearchRequest(BaseModel):
    source_station_id: int
    destination_station_id: int
    travel_date: date

class TrainSearchResponse(BaseModel):
    schedule_id: int
    train: Train
    route: Route
    schedule_date: date
    available_seats: int
    departure_time: time
    arrival_time: time
    base_fare: Decimal
    
    model_config = ConfigDict(from_attributes=True)

# Passenger schemas
class PassengerBase(BaseModel):
    name: str
    age: int
    gender: Gender

class PassengerCreate(PassengerBase):
    pass

class Passenger(PassengerBase):
    id: int
    seat_number: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Booking schemas
class BookingCreate(BaseModel):
    schedule_id: int
    passengers: List[PassengerCreate]

class Booking(BaseModel):
    id: int
    booking_reference: str
    passenger_count: int
    total_amount: Decimal
    status: BookingStatus
    booking_date: datetime
    journey_date_from: date
    journey_date_to: date
    schedule: "TrainScheduleResponse"
    passengers: List[Passenger]
    
    model_config = ConfigDict(from_attributes=True)

class TrainScheduleResponse(BaseModel):
    id: int
    schedule_date: date
    available_seats: int
    route: Route
    
    model_config = ConfigDict(from_attributes=True)

# Update forward references
Booking.model_rebuild()

class RefundStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RefundRequestBase(BaseModel):
    booking_id: int
    user_id: int
    amount: Decimal
    status: RefundStatus
    requested_at: datetime
    approved_at: Optional[datetime]
    admin_id: Optional[int]
    rejection_reason: Optional[str]

class RefundRequestCreate(BaseModel):
    booking_id: int
    amount: Decimal

class RefundRequest(RefundRequestBase):
    id: int
    booking: Booking
    user: User
    admin: Optional[User]
    
    model_config = ConfigDict(from_attributes=True)

# Update forward references
RefundRequest.model_rebuild()

class RefundRequestUpdate(BaseModel):
    status: RefundStatus
    rejection_reason: Optional[str] = None