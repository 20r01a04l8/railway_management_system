# Quick Start Guide - Railway Management System

## Prerequisites
- Python 3.8+ installed
- MySQL 8.0+ installed and running
- Modern web browser

## 5-Minute Setup

### 1. Database Setup (2 minutes)
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE railway_db;
exit;

# Import schema and data
mysql -u root -p railway_db < database/schema.sql
mysql -u root -p railway_db < database/sample_data.sql
```

### 2. Backend Setup (2 minutes)
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update .env file with your MySQL password
# Edit .env and change the DATABASE_URL

# Start backend
python main.py
```

### 3. Frontend Setup (1 minute)
```bash
cd frontend

# Start frontend server
python -m http.server 3000
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Default Login Credentials

### Admin Account
- Email: `admin@railway.com`
- Password: `admin123`

### User Account
- Email: `user@example.com`
- Password: `user123`

## Test the System

1. **Register**: Create a new user account
2. **Login**: Use your credentials or default accounts
3. **Search**: Look for trains between Delhi (DEL) and Mumbai (MUM)
4. **Book**: Select a train and book tickets for passengers
5. **Manage**: View and cancel bookings in "My Bookings"

## Troubleshooting

### Database Connection Error
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Update .env file with correct credentials
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/railway_db
```

### Python Import Errors
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### CORS Errors
- Make sure frontend is running on port 3000
- Backend should be on port 8000
- Check browser console for specific errors

## Next Steps

1. **Customize**: Modify the code to add new features
2. **Deploy**: Use the production deployment guide in README.md
3. **Extend**: Add payment integration, seat selection, etc.

## Support

- Check the full README.md for detailed documentation
- Review API documentation at http://localhost:8000/docs
- Check database design in docs/database-design.md