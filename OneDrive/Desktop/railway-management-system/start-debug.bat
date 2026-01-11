@echo off
echo Starting Railway Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Start the backend server
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo.
start /b python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Open the debug frontend
echo Opening debug frontend...
cd /d "%~dp0frontend"
start debug.html

echo.
echo ========================================
echo Railway Management System is starting!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend: debug.html (opened in browser)
echo.
echo Press any key to stop the backend server...
pause >nul

REM Kill the backend process
taskkill /f /im python.exe >nul 2>&1
echo Backend server stopped.