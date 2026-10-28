@echo off
echo ============================================
echo   PaperLensAI - Opening Frontend
echo ============================================
echo.
echo Make sure backend is running first!
echo Backend URL: http://localhost:8000/api/docs
echo.
start "" "%~dp0frontend\index.html"
echo Frontend opened in browser!
timeout /t 2
