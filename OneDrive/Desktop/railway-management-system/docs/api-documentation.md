# Railway Management System - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00.000Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Email already registered"
}
```

#### POST /auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huLmRvZUBleGFtcGxlLmNvbSIsImV4cCI6MTcwNDEwMjAwMH0.signature",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "phone": "+91-9876543210",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect email or password"
}
```

### 2. Stations

#### GET /stations/
Get all railway stations.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "DEL",
    "name": "New Delhi",
    "city": "Delhi",
    "state": "Delhi",
    "created_at": "2024-01-01T00:00:00.000Z"
  },
  {
    "id": 2,
    "code": "MUM",
    "name": "Mumbai Central",
    "city": "Mumbai",
    "state": "Maharashtra",
    "created_at": "2024-01-01T00:00:00.000Z"
  }
]
```

#### POST /stations/ (Admin Only)
Create a new railway station.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "code": "BLR",
  "name": "Bangalore City",
  "city": "Bangalore",
  "state": "Karnataka"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "code": "BLR",
  "name": "Bangalore City",
  "city": "Bangalore",
  "state": "Karnataka",
  "created_at": "2024-01-01T10:00:00.000Z"
}
```

#### GET /stations/{station_id}
Get station details by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "code": "DEL",
  "name": "New Delhi",
  "city": "Delhi",
  "state": "Delhi",
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

### 3. Trains

#### GET /trains/
Get all active trains.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "number": "12001",
    "name": "Shatabdi Express",
    "type": "superfast",
    "total_seats": 200,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000Z"
  },
  {
    "id": 2,
    "number": "12002",
    "name": "Rajdhani Express",
    "type": "superfast",
    "total_seats": 300,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000Z"
  }
]
```

#### POST /trains/ (Admin Only)
Create a new train.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "number": "12003",
  "name": "Duronto Express",
  "type": "express",
  "total_seats": 250
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "number": "12003",
  "name": "Duronto Express",
  "type": "express",
  "total_seats": 250,
  "is_active": true,
  "created_at": "2024-01-01T10:00:00.000Z"
}
```

#### POST /trains/search
Search for available trains between stations.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "source_station_id": 1,
  "destination_station_id": 2,
  "travel_date": "2024-01-15"
}
```

**Response (200 OK):**
```json
[
  {
    "schedule_id": 1,
    "train": {
      "id": 1,
      "number": "12001",
      "name": "Shatabdi Express",
      "type": "superfast",
      "total_seats": 200,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00.000Z"
    },
    "route": {
      "id": 1,
      "train_id": 1,
      "source_station_id": 1,
      "destination_station_id": 2,
      "departure_time": "06:00:00",
      "arrival_time": "14:30:00",
      "distance_km": 1384,
      "base_fare": 2500.00,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00.000Z",
      "train": { /* train object */ },
      "source_station": {
        "id": 1,
        "code": "DEL",
        "name": "New Delhi",
        "city": "Delhi",
        "state": "Delhi"
      },
      "destination_station": {
        "id": 2,
        "code": "MUM",
        "name": "Mumbai Central",
        "city": "Mumbai",
        "state": "Maharashtra"
      }
    },
    "schedule_date": "2024-01-15",
    "available_seats": 150,
    "departure_time": "06:00:00",
    "arrival_time": "14:30:00",
    "base_fare": 2500.00
  }
]
```

### 4. Routes

#### GET /routes/
Get all active routes.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "train_id": 1,
    "source_station_id": 1,
    "destination_station_id": 2,
    "departure_time": "06:00:00",
    "arrival_time": "14:30:00",
    "distance_km": 1384,
    "base_fare": 2500.00,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000Z",
    "train": {
      "id": 1,
      "number": "12001",
      "name": "Shatabdi Express",
      "type": "superfast"
    },
    "source_station": {
      "id": 1,
      "code": "DEL",
      "name": "New Delhi"
    },
    "destination_station": {
      "id": 2,
      "code": "MUM",
      "name": "Mumbai Central"
    }
  }
]
```

#### POST /routes/ (Admin Only)
Create a new route.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "train_id": 1,
  "source_station_id": 1,
  "destination_station_id": 3,
  "departure_time": "08:00:00",
  "arrival_time": "20:30:00",
  "distance_km": 2168,
  "base_fare": 3200.00
}
```

### 5. Bookings

#### POST /bookings/
Create a new booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "schedule_id": 1,
  "passengers": [
    {
      "name": "John Doe",
      "age": 30,
      "gender": "male"
    },
    {
      "name": "Jane Doe",
      "age": 28,
      "gender": "female"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "booking_reference": "RMS12345",
  "passenger_count": 2,
  "total_amount": 5000.00,
  "status": "confirmed",
  "booking_date": "2024-01-01T10:00:00.000Z",
  "schedule": {
    "id": 1,
    "schedule_date": "2024-01-15",
    "available_seats": 148,
    "route": {
      "id": 1,
      "departure_time": "06:00:00",
      "arrival_time": "14:30:00",
      "base_fare": 2500.00,
      "train": {
        "id": 1,
        "number": "12001",
        "name": "Shatabdi Express"
      },
      "source_station": {
        "name": "New Delhi"
      },
      "destination_station": {
        "name": "Mumbai Central"
      }
    }
  },
  "passengers": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 30,
      "gender": "male",
      "seat_number": null
    },
    {
      "id": 2,
      "name": "Jane Doe",
      "age": 28,
      "gender": "female",
      "seat_number": null
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Insufficient seats available"
}
```

#### GET /bookings/
Get current user's bookings.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "booking_reference": "RMS12345",
    "passenger_count": 2,
    "total_amount": 5000.00,
    "status": "confirmed",
    "booking_date": "2024-01-01T10:00:00.000Z",
    "schedule": {
      "id": 1,
      "schedule_date": "2024-01-15",
      "available_seats": 148,
      "route": {
        "train": {
          "name": "Shatabdi Express",
          "number": "12001"
        },
        "source_station": {
          "name": "New Delhi"
        },
        "destination_station": {
          "name": "Mumbai Central"
        }
      }
    },
    "passengers": [
      {
        "name": "John Doe",
        "age": 30,
        "gender": "male"
      }
    ]
  }
]
```

#### PUT /bookings/{booking_id}/cancel
Cancel a booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "booking_reference": "RMS12345",
  "passenger_count": 2,
  "total_amount": 5000.00,
  "status": "cancelled",
  "booking_date": "2024-01-01T10:00:00.000Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Booking not found"
}
```

## Error Responses

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

Currently no rate limiting is implemented, but in production you should consider:
- 100 requests per minute per IP for public endpoints
- 1000 requests per minute per authenticated user
- 10 requests per minute for registration endpoint

## Pagination

For endpoints that return lists, pagination can be implemented:

```
GET /bookings/?skip=0&limit=10
```

## Sample cURL Commands

### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User",
    "phone": "+91-1234567890"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

### Search Trains
```bash
curl -X POST "http://localhost:8000/trains/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "source_station_id": 1,
    "destination_station_id": 2,
    "travel_date": "2024-01-15"
  }'
```

### Create Booking
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "schedule_id": 1,
    "passengers": [
      {
        "name": "John Doe",
        "age": 30,
        "gender": "male"
      }
    ]
  }'
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from the browser.