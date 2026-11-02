@echo off
title Launching GigsSTRACK App...
echo ===================================================
echo   Menjalankan Server GigsSTRACK (Backend + Frontend)
echo ===================================================

echo [1/3] Menjalankan Django Backend...
start "GigsSTRACK Backend (Django)" cmd /k "cd /d "%~dp0backend" && .\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

echo [2/3] Menjalankan Vite Frontend...
start "GigsSTRACK Frontend (React)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [3/3] Menjalankan Telegram Bot Worker...
start "GigsSTRACK Telegram Bot" cmd /k "cd /d "%~dp0backend" && .\venv\Scripts\python.exe manage.py run_telegram_bot"

echo.
echo GigsSTRACK Berhasil Dijalankan!
echo - Backend API: http://127.0.0.1:8000/api/
echo - Frontend Web: http://localhost:5173/
echo - Telegram Bot Worker: ACTIVE
echo.

