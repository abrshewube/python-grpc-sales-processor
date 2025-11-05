@echo off
REM Quick script to start backend services manually

echo ========================================
echo Starting Backend Services
echo ========================================
echo.

cd backend
call venv\Scripts\activate.bat

echo Starting gRPC server in new window...
start cmd /k "cd backend && call venv\Scripts\activate.bat && python server.py"

timeout /t 2 /nobreak >nul

echo Starting HTTP proxy in new window...
start cmd /k "cd backend && call venv\Scripts\activate.bat && python http_proxy.py"

echo.
echo ========================================
echo Both services started!
echo - gRPC server: localhost:50051
echo - HTTP proxy: http://localhost:8000
echo ========================================
echo.
echo Press any key to exit...
pause >nul

