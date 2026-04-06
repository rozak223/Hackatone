@echo off
REM SYNCHAIN AI - Real-time Monitoring Quick Start
REM Run this to start the dashboard

title SYNCHAIN AI - Real-time Monitoring Dashboard

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║                                                    ║
echo ║     🚀 SYNCHAIN AI - Real-time Monitoring        ║
echo ║                                                    ║
echo ║        Starting Dashboard Server...              ║
echo ║                                                    ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Activate virtual environment
echo Installing dependencies...
.venv\Scripts\pip install flask flask-cors -q

REM Start the server
echo.
echo ✅ Starting SYNCHAIN AI Dashboard...
echo.
echo 🌐 Dashboard URL: http://localhost:5000
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  Press Ctrl+C to stop the server                 ║
echo ║  Open browser and go to http://localhost:5000    ║
echo ╚════════════════════════════════════════════════════╝
echo.

.venv\Scripts\python.exe realtime_dashboard.py

pause