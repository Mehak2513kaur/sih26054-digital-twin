@echo off
title DRDO UAV Digital Twin Backend (FastAPI + Simulation)
cd /d "%~dp0"
echo Starting UAV Digital Twin Backend on http://localhost:8000 ...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
