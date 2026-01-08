@echo off
echo Stopping Church Agent...
taskkill /F /IM python.exe
echo.
echo Server Stopped.
timeout /t 2 >nul