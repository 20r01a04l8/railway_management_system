@echo off
echo ========================================
echo Railway Management System Setup
echo ========================================

echo.
echo Step 1: Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo.
echo Step 2: Installing Python dependencies...
pip install --upgrade pip
echo Trying to install with pre-compiled wheels...
pip install --only-binary=all -r requirements.txt
if %errorlevel% neq 0 (
    echo Installation failed, trying fallback requirements...
    pip install -r requirements-fallback.txt
)

echo.
echo Step 3: Database setup instructions...
echo Please ensure MySQL is running and execute the following commands:
echo.
echo 1. Create database:
echo    mysql -u root -p -e "CREATE DATABASE railway_db;"
echo.
echo 2. Import schema:
echo    mysql -u root -p railway_db ^< ..\database\schema.sql
echo.
echo 3. Import sample data:
echo    mysql -u root -p railway_db ^< ..\database\sample_data.sql
echo.
echo 4. Update .env file with your database credentials

echo.
echo Step 4: Starting the application...
echo Backend will start on http://localhost:8000
echo Frontend will start on http://localhost:3000
echo.

pause

echo Starting backend server...
start cmd /k "cd /d %cd% && call venv\Scripts\activate && python main.py"

echo Starting frontend server...
cd ..\frontend
start cmd /k "python -m http.server 3000"

echo.
echo Setup complete! 
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Default credentials:
echo Admin: admin@railway.com / admin123
echo User: user@example.com / user123

pause