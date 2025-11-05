@echo off
REM Generate Python code from proto files (Windows)
REM This script activates the venv and regenerates proto files

cd backend

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found at backend\venv
    echo Using system Python instead...
)

REM Generate proto files
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto

REM Fix imports in generated files
python fix_proto_imports.py

echo.
echo Proto files generated successfully!
echo Files created in backend/proto/:
echo   - sales_pb2.py
echo   - sales_pb2_grpc.py
echo.
pause

