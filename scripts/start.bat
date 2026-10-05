@echo off
echo ============================================
echo  Deepfake Detector - Local Startup
echo ============================================
echo.
echo WARNING: Docker deployment is RECOMMENDED!
echo This script is for advanced users only.
echo.
pause

REM Navigate to project root
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.11+ is installed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r configs\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if model weights exist
if not exist "models\trufor.pth.tar" (
    echo ERROR: models\trufor.pth.tar not found!
    echo Please download model weights first.
    echo See: WEIGHTS_DOWNLOAD_GUIDE.md
    pause
    exit /b 1
)

REM Start the server
echo.
echo Starting server...
echo Access at: http://localhost:8000/web/index_main.html
echo.
python scripts\start_trufor.py

pause


