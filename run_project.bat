@echo off
REM ===================================
REM Django LMS Insights Project Runner
REM ===================================

cls
echo.
echo ====================================
echo Django LMS Insights - Complete Run
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [1/6] Python found: 
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo [2/6] Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.
echo.

REM Install dependencies
echo [4/6] Installing dependencies from requirements.txt...
python -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed. Please free disk space and try again.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.

REM Apply migrations
echo [5/6] Applying database migrations...
python manage.py migrate --noinput
echo Migrations applied.
echo.

REM Run the development server
echo [6/6] Starting Django development server...
echo.
echo ====================================
echo Server is running at http://127.0.0.1:8000/
echo Press CTRL+C to stop the server
echo ====================================
echo.

python manage.py runserver

pause
