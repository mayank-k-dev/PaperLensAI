@echo off
echo ============================================
echo   PaperLensAI - Starting Backend Server
echo ============================================
echo.
cd /d "%~dp0backend"

REM Try to use conda python first, then fall back to py launcher
where conda >nul 2>&1
if %errorlevel% == 0 (
    echo Using Anaconda Python...
    call conda activate base 2>nul
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo Using system Python...
    py -3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
)

pause
