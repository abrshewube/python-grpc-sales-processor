@echo off
echo ========================================
echo Backend Setup Script
echo ========================================
echo.

REM Check if venv exists
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
    echo Virtual environment created!
    echo.
)

echo Activating virtual environment...
cd backend
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
echo Attempting to install with pre-built wheels...
python -m pip install --only-binary :all: grpcio grpcio-tools protobuf flask flask-cors || pip install -r requirements.txt

echo.
echo Generating proto files...
python -m grpc_tools.protoc -I proto --python_out=proto --grpc_python_out=proto proto/sales.proto

echo Fixing proto imports...
python fix_proto_imports.py

echo.
echo Creating storage directory...
if not exist "storage\processed" mkdir storage\processed

echo.
echo ========================================
echo Starting backend services...
echo ========================================
echo.
echo Starting gRPC server (Terminal 1)...
start cmd /k "cd backend && call venv\Scripts\activate.bat && python server.py"
timeout /t 3 /nobreak >nul

echo Starting HTTP proxy (Terminal 2)...
start cmd /k "cd backend && call venv\Scripts\activate.bat && python http_proxy.py"

echo.
echo ========================================
echo Backend services started!
echo - gRPC server: localhost:50051
echo - HTTP proxy: http://localhost:8000
echo ========================================
echo.
pause
