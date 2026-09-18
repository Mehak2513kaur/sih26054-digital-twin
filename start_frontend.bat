@echo off
title DRDO UAV Digital Twin Operator Dashboard (Vite)
cd /d "%~dp0frontend"
echo Starting UAV Digital Twin Operator Console on http://localhost:5173 ...
npm run dev
pause
