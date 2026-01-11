# Railway Management System - Database Design

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     USERS       │       │    STATIONS     │       │     TRAINS      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ email           │       │ code            │       │ number          │
│ password_hash   │       │ name            │       │ name            │
│ full_name       │       │ city            │       │ type            │
│ phone           │       │ state           │       │ total_seats     │
│ role            │       │ created_at      │       │ is_active       │
│ is_active       │       └─────────────────┘       │ created_at      │
│ created_at      │                                 └─────────────────┘
│ updated_at      │                                          │
└─────────────────┘                                          │
         │                                                   │
         │                                                   │
         │ 1:N                                               │ 1:N
         │                                                   │
         ▼                                                   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    BOOKINGS     │       │     ROUTES      │◄──────┤ TRAIN_SCHEDULES │
├─────────────────┤       ├─────────────────┤  1:N  ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ train_id (FK)   │       │ route_id (FK)   │
│ schedule_id(FK) │       │ source_stn(FK)  │       │ schedule_date   │
│ booking_ref     │       │ dest_stn (FK)   │       │ available_seats │
│ passenger_count │       │ departure_time  │       │ status          │
│ total_amount    │       │ arrival_time    │       │ created_at      │
│ status          │       │ distance_km     │       └─────────────────┘
│ booking_date    │       │ base_fare       │                │
└─────────────────┘       │ is_active       │                │
         │                │ created_at      │                │ N:1
         │ 1:N            └─────────────────┘                │
         │                         │                         │
         ▼                         │ N:1                     │
┌─────────────────┐                │                         │
│   PASSENGERS    │                ▼                         │
├─────────────────┤       ┌─────────────────┐                │
│ id (PK)         │       │    STATIONS     │◄───────────────┘
│ booking_id (FK) │       │  (Source/Dest)  │
│ name            │       └─────────────────┘
│ age             │
│ gender          │
│ seat_number     │
└─────────────────┘
```

## Table Relationships

### Primary Relationships

1. **Users → Bookings** (1:N)
   - One user can have multiple bookings
   - Each booking belongs to one user

2. **Trains → Routes** (1:N)
   - One train can have multiple routes
   - Each route belongs to one train

3. **Routes → Train Schedules** (1:N)
   - One route can have multiple schedules (different dates)
   - Each schedule belongs to one route

4. **Train Schedules → Bookings** (1:N)
   - One schedule can have multiple bookings
   - Each booking is for one specific schedule

5. **Bookings → Passengers** (1:N)
   - One booking can have multiple passengers
   - Each passenger belongs to one booking

6. **Stations → Routes** (N:M via Foreign Keys)
   - Each route has source and destination stations
   - Stations can be source/destination for multiple routes

### Key Constraints

- **Unique Constraints**: User emails, train numbers, station codes, booking references
- **Foreign Key Constraints**: Maintain referential integrity
- **Check Constraints**: Ensure valid data (e.g., positive ages, valid enum values)
- **Composite Unique**: Route + Schedule Date combination

### Normalization Level

The database follows **Third Normal Form (3NF)**:

1. **1NF**: All attributes contain atomic values
2. **2NF**: No partial dependencies on composite keys
3. **3NF**: No transitive dependencies

### Indexes for Performance

```sql
-- Primary indexes (automatic)
PRIMARY KEY indexes on all id columns

-- Unique indexes
UNIQUE INDEX on users.email
UNIQUE INDEX on trains.number
UNIQUE INDEX on stations.code
UNIQUE INDEX on bookings.booking_reference
UNIQUE INDEX on (train_schedules.route_id, train_schedules.schedule_date)

-- Performance indexes
INDEX on routes.train_id
INDEX on train_schedules.schedule_date
INDEX on bookings.user_id
INDEX on passengers.booking_id
```

## Business Rules Implemented

1. **User Management**
   - Email must be unique
   - Passwords are hashed using bcrypt
   - Role-based access control (admin/user)

2. **Train Operations**
   - Train numbers must be unique
   - Trains can be activated/deactivated
   - Multiple routes per train allowed

3. **Route Management**
   - Routes define train paths between stations
   - Include timing and fare information
   - Can be activated/deactivated

4. **Scheduling**
   - Schedules are created for specific dates
   - Track available seats per schedule
   - Prevent overbooking through constraints

5. **Booking System**
   - Generate unique booking references
   - Support multiple passengers per booking
   - Transaction safety for seat allocation
   - Booking status tracking

6. **Data Integrity**
   - Cascading deletes for dependent records
   - Foreign key constraints prevent orphaned records
   - Enum constraints for status fields

## Sample Queries

### Find Available Trains
```sql
SELECT ts.*, t.name, t.number, r.departure_time, r.arrival_time, r.base_fare
FROM train_schedules ts
JOIN routes r ON ts.route_id = r.id
JOIN trains t ON r.train_id = t.id
WHERE r.source_station_id = 1 
  AND r.destination_station_id = 2
  AND ts.schedule_date = '2024-01-15'
  AND ts.available_seats > 0
  AND r.is_active = TRUE
  AND t.is_active = TRUE;
```

### User Booking History
```sql
SELECT b.*, t.name as train_name, t.number as train_number,
       ss.name as source_station, ds.name as dest_station
FROM bookings b
JOIN train_schedules ts ON b.schedule_id = ts.id
JOIN routes r ON ts.route_id = r.id
JOIN trains t ON r.train_id = t.id
JOIN stations ss ON r.source_station_id = ss.id
JOIN stations ds ON r.destination_station_id = ds.id
WHERE b.user_id = 1
ORDER BY b.booking_date DESC;
```

### Revenue Report
```sql
SELECT t.name, t.number, 
       COUNT(b.id) as total_bookings,
       SUM(b.total_amount) as total_revenue,
       SUM(b.passenger_count) as total_passengers
FROM bookings b
JOIN train_schedules ts ON b.schedule_id = ts.id
JOIN routes r ON ts.route_id = r.id
JOIN trains t ON r.train_id = t.id
WHERE b.status = 'confirmed'
  AND b.booking_date >= '2024-01-01'
GROUP BY t.id, t.name, t.number
ORDER BY total_revenue DESC;
```