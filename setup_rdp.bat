@echo off
REM Setup script for Windows RDP deployment
echo ========================================
echo Quotex API Setup for Windows RDP
echo ========================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.11 first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Installing Playwright browsers...
playwright install chromium
playwright install-deps chromium

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the API server:
echo   python api_server.py
echo.
echo To run as Windows Service:
echo   1. Open Task Scheduler
echo   2. Create Basic Task
echo   3. Set to run at startup
echo   4. Action: python.exe api_server.py
echo.
echo Your API will be available at:
echo   http://YOUR_RDP_IP:8000
echo.
pause
