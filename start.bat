@echo off
chcp 65001 >nul
cls
color 0B

echo ===================================
echo   CHURCH AGENT (BACKGROUND MODE)
echo ===================================

:: 1. Перевірка та розблокування
echo [1/3] Unblocking tools...
powershell -Command "Unblock-File -Path '%~dp0nircmd.exe' -ErrorAction SilentlyContinue"

:: 2. Бібліотеки
echo [2/3] Checking libraries...
pip install fastapi uvicorn psutil >nul 2>&1

:: 3. ПРИХОВАНИЙ ЗАПУСК
echo.
echo [3/3] Starting Server Hidden...
echo.
echo    Server is starting on Port 8001.
echo    This window will close in 3 seconds.
echo    To stop the server, run STOP.bat
echo.

:: Використовуємо nircmd для запуску без вікна
"%~dp0nircmd.exe" exec hide python "%~dp0main.py"

:: Чекаємо 3 секунди і закриваємо це вікно
timeout /t 3 >nul
exit