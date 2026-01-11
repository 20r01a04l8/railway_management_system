# Railway Management System

A comprehensive railway booking and management system built with FastAPI (Python) backend, React frontend, and MySQL database.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Train Search**: Search trains between stations with real-time availability
- **Booking Management**: Book tickets for multiple passengers with transaction safety
- **User Dashboard**: View and manage bookings
- **Admin Panel**: Manage trains, routes, and stations (Admin only)
- **Responsive UI**: Modern React-based user interface

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **MySQL**: Relational database
- **JWT**: Authentication tokens
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: JavaScript library for UI
- **React Router**: Client-side routing
- **Bootstrap**: CSS framework
- **Fetch API**: HTTP client

### Database
- **MySQL**: Normalized schema with proper relationships
- **Indexes**: Optimized for performance

## Project Structure

```
railway-management-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── stations.py      # Station management
│   │   │   ├── trains.py        # Train operations
│   │   │   ├── routes.py        # Route management
│   │   │   └── bookings.py      # Booking operations
│   │   ├── core/
│   │   │   ├── database.py      # Database configuration
│   │   │   └── security.py      # Security utilities
│   │   ├── models/
│   │   │   └── __init__.py      # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── __init__.py      # Pydantic schemas
│   │   └── services/
│   │       └── __init__.py      # Business logic
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── frontend/
│   └── index.html              # React application
├── database/
│   ├── schema.sql              # Database schema
│   └── sample_data.sql         # Sample data
└── docs/
    └── README.md               # This file
```

## Database Schema

### ER Diagram Description

The database follows a normalized design with the following entities:

1. **Users**: Store user authentication and profile information
2. **Stations**: Railway stations with unique codes
3. **Trains**: Train information with capacity
4. **Routes**: Train routes between stations with timing and fare
5. **Train Schedules**: Specific train runs on specific dates
6. **Bookings**: User bookings with reference numbers
7. **Passengers**: Individual passenger details for each booking

### Key Relationships

- Users → Bookings (One-to-Many)
- Trains → Routes (One-to-Many)
- Routes → Train Schedules (One-to-Many)
- Train Schedules → Bookings (One-to-Many)
- Bookings → Passengers (One-to-Many)
- Stations → Routes (Many-to-Many via source/destination)

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Modern web browser

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd railway-management-system
```

### Step 2: Database Setup

1. **Create MySQL Database**:
```sql
CREATE DATABASE railway_db;
```

2. **Run Schema**:
```bash
mysql -u root -p railway_db < database/schema.sql
```

3. **Insert Sample Data**:
```bash
mysql -u root -p railway_db < database/sample_data.sql
```

### Step 3: Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Edit `.env` file with your database credentials:
```
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/railway_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Start the backend server**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Step 4: Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Serve the HTML file**:
You can use any static file server. For example:

**Using Python**:
```bash
python -m http.server 3000
```

**Using Node.js (if you have it)**:
```bash
npx serve -s . -l 3000
```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Authentication Endpoints

#### POST /auth/register
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST /auth/login
Authenticate user and get access token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

### Train Search

#### POST /trains/search
Search for available trains.

**Request**:
```json
{
  "source_station_id": 1,
  "destination_station_id": 2,
  "travel_date": "2024-01-15"
}
```

**Response**:
```json
[
  {
    "schedule_id": 1,
    "train": {
      "id": 1,
      "number": "12001",
      "name": "Shatabdi Express",
      "type": "superfast"
    },
    "route": {
      "departure_time": "06:00:00",
      "arrival_time": "14:30:00",
      "base_fare": 2500.00
    },
    "available_seats": 150,
    "schedule_date": "2024-01-15"
  }
]
```

### Booking

#### POST /bookings/
Create a new booking.

**Request**:
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

**Response**:
```json
{
  "id": 1,
  "booking_reference": "ABC12345",
  "passenger_count": 2,
  "total_amount": 5000.00,
  "status": "confirmed",
  "booking_date": "2024-01-01T10:00:00"
}
```


## Security Features

1. **Password Hashing**: Bcrypt for secure password storage
2. **JWT Tokens**: Secure authentication with expiration
3. **Role-based Access**: Admin and User roles with different permissions
4. **Input Validation**: Pydantic schemas for request validation
5. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
6. **CORS Configuration**: Proper CORS setup for frontend-backend communication

## Production Deployment

### Environment Variables
Update the following for production:

```env
DATABASE_URL=mysql+pymysql://user:password@production-db:3306/railway_db
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Optimizations
1. Add proper indexes (already included in schema)
2. Configure connection pooling
3. Set up database backups
4. Monitor query performance

### Security Hardening
1. Use HTTPS in production
2. Implement rate limiting
3. Add request logging
4. Set up monitoring and alerts
5. Regular security updates

## Testing

### Sample API Requests

You can test the API using curl or Postman:

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User",
    "phone": "+91-1234567890"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Search trains (requires authentication)
curl -X POST "http://localhost:8000/trains/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "source_station_id": 1,
    "destination_station_id": 2,
    "travel_date": "2024-01-15"
  }'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **CORS Errors**:
   - Check frontend URL is in CORS allowed origins
   - Verify API base URL in frontend

3. **Authentication Issues**:
   - Check JWT secret key configuration
   - Verify token expiration settings

4. **Import Errors**:
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

### Logs and Debugging

- Backend logs are printed to console
- Check browser developer tools for frontend errors
- Use MySQL logs for database issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the repository.