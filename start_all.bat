@echo off
title DRDO 26054 UAV Digital Twin Platform Launcher
echo ======================================================================
echo    DRDO PROBLEM STATEMENT 26054: AI DIGITAL TWIN FOR UAV ENGINES
echo               [SIMULATION MODE - ROTAX 915 iS CLASS]
echo ======================================================================
cd /d "%~dp0"
start "UAV Backend (Port 8000)" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "UAV Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"
echo.
echo Both services launched!
echo - Backend API & Docs: http://localhost:8000/docs
echo - Operator Dashboard: http://localhost:5173
echo.
