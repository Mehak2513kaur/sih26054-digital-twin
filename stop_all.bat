@echo off
title DRDO 26054 UAV Digital Twin - Stop All Services
echo ======================================================================
echo    STOPPING ALL DRDO 26054 UAV DIGITAL TWIN SERVICES
echo ======================================================================
echo.

echo Stopping backend (uvicorn on port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F 2>nul
)

echo Stopping frontend dev server (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F 2>nul
)

echo Stopping any remaining node processes...
taskkill /IM node.exe /F 2>nul

echo.
echo All services stopped.
echo.
pause
