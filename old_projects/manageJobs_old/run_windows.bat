@echo off
TITLE Luckfox Server (Windows Mode)
CLS

echo ==========================================
echo    LUCKFOX SERVER - WINDOWS LAUNCHER (FOR DEBUG)
echo ==========================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit
)

:: 2. Setup Virtual Environment
IF NOT EXIST "kuro_win" (
    echo [INFO] Creating Virtual Environment (kuro_win)...
    python -m venv kuro_win
)

:: 3. Activate and Install
echo [INFO] Activating Environment...
call kuro_win\Scripts\activate

echo [INFO] Checking Dependencies...
:: We use a temporary requirements file to exclude Gunicorn (doesn't work on Windows)
type requirements.txt | findstr /v "gunicorn" > requirements_win.txt
pip install -r requirements_win.txt >nul

:: 4. Start Server
echo.
echo [SUCCESS] Starting Server on http://127.0.0.1:8000
echo (Press Ctrl+C to stop)
echo.

:: Run standard Flask development server (since Gunicorn is Linux-only)
python run.py

pause