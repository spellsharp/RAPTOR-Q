@echo off
title RAPTOR-Q Startup Script
color 0A

echo.
echo ========================================
echo    RAPTOR-Q - Question Paper Generator
echo ========================================
echo.

:: Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo ✓ Python is installed

:: Check if Node.js is installed
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js is installed

:: Check if backend directory exists
echo [3/5] Checking project structure...
if not exist "app\backend\app.py" (
    echo ERROR: Backend files not found
    echo Make sure you're running this from the project root directory
    pause
    exit /b 1
)
echo ✓ Backend files found

:: Check if frontend directory exists
if not exist "app\frontend\package.json" (
    echo ERROR: Frontend files not found
    echo Make sure you're running this from the project root directory
    pause
    exit /b 1
)
echo ✓ Frontend files found

:: Check if .env file exists
echo [4/5] Checking configuration...
if not exist ".env" (
    echo WARNING: .env file not found
    echo You may need to create it with your API keys
    echo See WINDOWS_SETUP.md for details
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

:: Install dependencies if node_modules doesn't exist
if not exist "app\frontend\node_modules" (
    echo Installing frontend dependencies...
    cd app\frontend
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install frontend dependencies
        cd ..\..
        pause
        exit /b 1
    )
    cd ..\..
    echo ✓ Frontend dependencies installed
)

echo [5/5] Starting RAPTOR-Q...
echo.

:: Start backend in a new window
echo Starting backend server...
start "RAPTOR-Q Backend" cmd /k "echo Starting RAPTOR-Q Backend... && cd app\backend && python app.py"

:: Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Start frontend in a new window
echo Starting frontend server...
start "RAPTOR-Q Frontend" cmd /k "echo Starting RAPTOR-Q Frontend... && cd app\frontend && npm start"

echo.
echo ========================================
echo    RAPTOR-Q is starting up!
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Frontend App: http://localhost:3000
echo.
echo Two new windows should have opened:
echo - Backend window (Python Flask server)
echo - Frontend window (React development server)
echo.
echo Wait for both servers to fully start, then open:
echo http://localhost:3000 in your browser
echo.
echo To stop the application:
echo 1. Close both server windows
echo 2. Or press Ctrl+C in each window
echo.
echo Troubleshooting:
echo - If ports are busy, check README.md
echo - If LMStudio errors, make sure it's running
echo - Check .env file for API keys
echo.
echo Press any key to exit this window...
pause >nul 