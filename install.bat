@echo off
REM Library Management System - Automated Installation Script
REM This script will install and run the app automatically

echo.
echo ========================================
echo   Library Management System Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully
echo.

REM Create data directory
if not exist "data" mkdir data
echo [OK] Data directory created
echo.

REM Start the application
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Starting the application...
echo.
echo The app will open at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
timeout /t 3

python app.py
pause
